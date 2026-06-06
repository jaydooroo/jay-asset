from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Iterable

from .config import ingest_provider, ingest_tickers, price_table_name
from .dynamodb_client import dynamodb_resource
from .external_provider import ExternalPriceRepository


def _log(message: str) -> None:
    print(f"[market-ingest] {message}", flush=True)


def _normalize_tickers(tickers: Iterable[str]) -> list[str]:
    return sorted(dict.fromkeys(str(ticker).strip().upper() for ticker in tickers if str(ticker).strip()))


def _price_provider():
    provider_name = ingest_provider()
    if provider_name == "tiingo":
        from .providers import TiingoPriceRepository

        return provider_name, TiingoPriceRepository()

    return provider_name, ExternalPriceRepository()


def run_dynamodb_price_ingest(tickers: Iterable[str] | None = None, lookback_days: int = 7) -> dict:
    """
    Download recent daily closes from the external provider and upsert them into DynamoDB.

    This is intentionally small and scheduler-friendly. Initial backfills can call the
    same function with a larger lookback window, while the daily EventBridge job can
    use the default 7-day window to catch missed market days/weekends.
    """
    selected_tickers = _normalize_tickers(tickers or ingest_tickers())
    if not selected_tickers:
        return {
            "ok": False,
            "error": "No tickers configured. Set MARKET_INGEST_TICKERS or pass tickers explicitly.",
        }

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=max(1, int(lookback_days)))

    provider_name, provider = _price_provider()
    _log(
        "Starting price ingest "
        f"provider={provider_name} "
        f"tickers={len(selected_tickers)} "
        f"start={start_date.strftime('%Y-%m-%d')} "
        f"end={end_date.strftime('%Y-%m-%d')}"
    )

    prices, failed = provider.get_close_prices(selected_tickers, start_date, end_date)
    if prices is None or prices.empty:
        _log(f"No price data downloaded provider={provider_name} failed={failed}")
        return {
            "ok": False,
            "error": "No price data downloaded",
            "provider": provider_name,
            "missing_tickers": failed,
        }

    _log(
        "Downloaded price frame "
        f"rows={len(prices)} "
        f"columns={len(prices.columns)} "
        f"missing={sorted(set(failed))}"
    )

    table = dynamodb_resource().Table(price_table_name())
    written = 0
    total_cells = int(prices.notna().sum().sum())
    _log(f"Writing rows to DynamoDB table={price_table_name()} items={total_cells}")

    with table.batch_writer(overwrite_by_pkeys=["ticker", "price_date"]) as batch:
        for price_date, row in prices.sort_index().iterrows():
            price_date_key = price_date.strftime("%Y-%m-%d")
            for ticker, close in row.dropna().items():
                batch.put_item(
                    Item={
                        "ticker": str(ticker).upper(),
                        "price_date": price_date_key,
                        "close": Decimal(str(float(close))),
                        "source": provider_name,
                        "updated_at": int(end_date.timestamp()),
                    }
                )
                written += 1
                if written % 500 == 0:
                    _log(f"Written {written}/{total_cells} items...")

    _log(f"Finished DynamoDB write rows_written={written}")

    return {
        "ok": True,
        "table": price_table_name(),
        "provider": provider_name,
        "tickers": selected_tickers,
        "rows_written": written,
        "missing_tickers": sorted(set(failed)),
    }

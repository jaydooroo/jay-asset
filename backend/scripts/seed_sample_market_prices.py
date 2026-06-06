from __future__ import annotations

import argparse
import math
import os
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market.config import price_table_name  # noqa: E402
from market.dynamodb_client import dynamodb_resource  # noqa: E402


DEFAULT_TICKERS = [
    "SPY",
    "QQQ",
    "IWM",
    "VGK",
    "EWJ",
    "EEM",
    "VNQ",
    "GLD",
    "DBC",
    "HYG",
    "LQD",
    "IEF",
]


def _parse_tickers(value: str | None) -> list[str]:
    if not value:
        return list(DEFAULT_TICKERS)
    return [part.strip().upper() for part in value.split(",") if part.strip()]


def _business_dates(days: int) -> list[date]:
    current = date.today()
    dates: list[date] = []
    while len(dates) < days:
        if current.weekday() < 5:
            dates.append(current)
        current -= timedelta(days=1)
    return list(reversed(dates))


def _synthetic_close(ticker: str, index: int, total: int) -> float:
    """
    Produce deterministic but non-flat sample prices.

    These are not real prices. They only exist to test the DynamoDB-backed
    strategy pipeline when external providers are unavailable.
    """
    seed = sum(ord(ch) for ch in ticker)
    base = 60.0 + (seed % 180)
    trend = 1.0 + ((seed % 9) - 3) * 0.00025
    seasonal = 1.0 + math.sin((index + seed) / 18.0) * 0.025
    drifted = base * (trend ** max(index, 0)) * seasonal

    # Give defensive bond-like assets a milder path.
    if ticker in {"IEF", "LQD", "HYG", "BIL", "SHY", "AGG", "TLT"}:
        drifted = base * ((1.00005 + (seed % 3) * 0.00003) ** max(index, 0))
        drifted *= 1.0 + math.sin((index + seed) / 30.0) * 0.01

    return round(max(drifted, 1.0), 6)


def seed_sample_prices(tickers: list[str], trading_days: int) -> dict:
    table = dynamodb_resource().Table(price_table_name())
    dates = _business_dates(max(2, trading_days))

    written = 0
    with table.batch_writer(overwrite_by_pkeys=["ticker", "price_date"]) as batch:
        for ticker in tickers:
            for idx, price_date in enumerate(dates):
                close = _synthetic_close(ticker, idx, len(dates))
                batch.put_item(
                    Item={
                        "ticker": ticker,
                        "price_date": price_date.isoformat(),
                        "close": Decimal(str(close)),
                        "source": "sample",
                        "updated_at": int(date.today().strftime("%Y%m%d")),
                    }
                )
                written += 1

    return {
        "ok": True,
        "table": price_table_name(),
        "tickers": tickers,
        "trading_days": len(dates),
        "rows_written": written,
        "source": "sample",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed sample daily close prices into DynamoDB Local.")
    parser.add_argument("--tickers", help="Comma-separated tickers. Defaults to PAA universe.")
    parser.add_argument("--trading-days", type=int, default=756, help="Approx. 3 years of business days.")
    args = parser.parse_args()

    os.environ.setdefault("MARKET_PRICE_TABLE", "jay-asset-daily-prices")
    os.environ.setdefault("MARKET_DYNAMODB_ENDPOINT_URL", "http://localhost:8000")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

    result = seed_sample_prices(
        tickers=_parse_tickers(args.tickers),
        trading_days=args.trading_days,
    )
    print(result)


if __name__ == "__main__":
    main()

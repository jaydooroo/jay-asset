from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
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
    "EFA",
    "AGG",
    "SHY",
    "REM",
    "TLT",
    "BIL",
]


def _parse_tickers(value: str | None) -> list[str]:
    if not value:
        return list(DEFAULT_TICKERS)
    return [part.strip().upper() for part in value.split(",") if part.strip()]


def _decimal_to_string(value) -> str:
    if isinstance(value, Decimal):
        return str(float(value))
    if value is None:
        return ""
    return str(value)


def inspect_ticker(table, ticker: str, sample_limit: int) -> dict:
    try:
        from boto3.dynamodb.conditions import Key
    except Exception as exc:
        raise RuntimeError("boto3 is required to inspect DynamoDB market prices") from exc

    items = []
    kwargs = {
        "KeyConditionExpression": Key("ticker").eq(ticker),
    }

    while True:
        response = table.query(**kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        kwargs["ExclusiveStartKey"] = last_key

    if not items:
        return {
            "ticker": ticker,
            "rows": 0,
            "first_date": "",
            "last_date": "",
            "sources": "",
            "latest_close": "",
        }

    items.sort(key=lambda item: item.get("price_date", ""))
    sources = Counter(str(item.get("source", "")) for item in items if item.get("source"))
    latest = items[-1]
    sample = items[-sample_limit:] if sample_limit > 0 else []

    return {
        "ticker": ticker,
        "rows": len(items),
        "first_date": items[0].get("price_date", ""),
        "last_date": latest.get("price_date", ""),
        "sources": ",".join(f"{source}:{count}" for source, count in sources.items()),
        "latest_close": _decimal_to_string(latest.get("close")),
        "sample": sample,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect market prices stored in DynamoDB.")
    parser.add_argument("--tickers", help="Comma-separated tickers. Defaults to all strategy tickers.")
    parser.add_argument("--sample-limit", type=int, default=0, help="Show latest N raw items per ticker.")
    args = parser.parse_args()

    os.environ.setdefault("MARKET_PRICE_TABLE", "jay-asset-daily-prices")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

    table = dynamodb_resource().Table(price_table_name())
    tickers = _parse_tickers(args.tickers)

    print(f"Table: {price_table_name()}")
    print(f"{'Ticker':<8} {'Rows':>6} {'First':<12} {'Last':<12} {'Latest Close':>14} {'Sources'}")
    print("-" * 80)

    total_rows = 0
    for ticker in tickers:
        result = inspect_ticker(table, ticker, args.sample_limit)
        total_rows += int(result["rows"])
        print(
            f"{result['ticker']:<8} "
            f"{result['rows']:>6} "
            f"{result['first_date']:<12} "
            f"{result['last_date']:<12} "
            f"{result['latest_close']:>14} "
            f"{result['sources']}"
        )

        if args.sample_limit > 0 and result.get("sample"):
            for item in result["sample"]:
                print(f"  sample {item}")

    print("-" * 80)
    print(f"Total rows: {total_rows}")


if __name__ == "__main__":
    main()

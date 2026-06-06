from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market.ingest import run_dynamodb_price_ingest  # noqa: E402


def _parse_tickers(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [part.strip().upper() for part in value.split(",") if part.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest daily close prices into DynamoDB.")
    parser.add_argument("--tickers", help="Comma-separated tickers, e.g. SPY,QQQ,IEF")
    parser.add_argument("--lookback-days", type=int, default=7)
    args = parser.parse_args()

    os.environ.setdefault("MARKET_PRICE_TABLE", "jay-asset-daily-prices")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

    result = run_dynamodb_price_ingest(
        tickers=_parse_tickers(args.tickers),
        lookback_days=args.lookback_days,
    )
    print(result)
    if not result.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

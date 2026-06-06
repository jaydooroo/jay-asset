from __future__ import annotations

import os


def price_source() -> str:
    """
    Select the runtime price source.

    Supported values:
      - external: current Stooq/Yahoo downloader
      - dynamodb: DynamoDB-backed historical close prices
    """
    return os.getenv("MARKET_PRICE_SOURCE", "external").strip().lower() or "external"


def ingest_provider() -> str:
    """
    Select the provider used by market-data ingestion jobs.

    Supported values:
      - external: current Stooq/Yahoo downloader
      - tiingo: Tiingo EOD API
    """
    return os.getenv("MARKET_INGEST_PROVIDER", "external").strip().lower() or "external"


def tiingo_api_key() -> str | None:
    value = os.getenv("TIINGO_API_KEY", "").strip()
    return value or None


def price_table_name() -> str:
    return os.getenv("MARKET_PRICE_TABLE", "jay-asset-daily-prices").strip() or "jay-asset-daily-prices"


def dynamodb_endpoint_url() -> str | None:
    value = os.getenv("MARKET_DYNAMODB_ENDPOINT_URL", "").strip()
    return value or None


def aws_region() -> str:
    return (
        os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "us-east-1"
    ).strip()


def ingest_tickers() -> list[str]:
    raw = os.getenv("MARKET_INGEST_TICKERS", "")
    return sorted(dict.fromkeys(part.strip().upper() for part in raw.split(",") if part.strip()))

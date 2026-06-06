from __future__ import annotations

import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market.config import dynamodb_endpoint_url, price_table_name  # noqa: E402
from market.dynamodb_client import dynamodb_resource  # noqa: E402


def _check_local_endpoint(endpoint: str | None) -> None:
    if not endpoint:
        return

    parsed = urlparse(endpoint)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if not host:
        return

    try:
        with socket.create_connection((host, port), timeout=3):
            return
    except OSError as exc:
        raise RuntimeError(
            f"Cannot connect to DynamoDB endpoint {endpoint}. "
            "If you are using DynamoDB Local, start it from the project root with: "
            "docker compose up -d dynamodb-local"
        ) from exc


def create_table_if_missing() -> None:
    table_name = price_table_name()
    endpoint = dynamodb_endpoint_url() or "AWS DynamoDB default endpoint"
    print(f"Using DynamoDB endpoint: {endpoint}", flush=True)
    print(f"Using table name: {table_name}", flush=True)
    _check_local_endpoint(dynamodb_endpoint_url())

    dynamodb = dynamodb_resource()

    existing = dynamodb.meta.client.list_tables().get("TableNames", [])
    if table_name in existing:
        print(f"Table already exists: {table_name}")
        return

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "ticker", "KeyType": "HASH"},
            {"AttributeName": "price_date", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "ticker", "AttributeType": "S"},
            {"AttributeName": "price_date", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print(f"Created table: {table_name}")


if __name__ == "__main__":
    os.environ.setdefault("MARKET_PRICE_TABLE", "jay-asset-daily-prices")
    os.environ.setdefault("MARKET_DYNAMODB_ENDPOINT_URL", "http://localhost:8000")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
    create_table_if_missing()

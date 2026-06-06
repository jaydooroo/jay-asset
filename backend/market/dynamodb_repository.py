from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable, List, Tuple

import pandas as pd

from .dynamodb_client import dynamodb_resource
from .config import price_table_name
from .repository import PriceRepository


def _to_float(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except Exception:
        return None


class DynamoDBPriceRepository(PriceRepository):
    """
    Price repository backed by DynamoDB.

    Expected table shape:
      - Partition key: ticker (String)
      - Sort key: price_date (String, YYYY-MM-DD)
      - Attribute: close (Number)

    This keeps strategy code independent from DynamoDB details.
    """

    def __init__(self, table_name: str | None = None):
        self.table_name = table_name or price_table_name()

    def _table(self):
        return dynamodb_resource().Table(self.table_name)

    def get_close_prices(
        self,
        tickers: Iterable[str],
        start_date: datetime,
        end_date: datetime,
    ) -> Tuple[pd.DataFrame, List[str]]:
        try:
            from boto3.dynamodb.conditions import Key
        except Exception as exc:  # pragma: no cover - depends on local/AWS runtime
            raise RuntimeError("boto3 DynamoDB conditions are required for price queries") from exc

        tickers_list = [str(ticker).strip().upper() for ticker in tickers if str(ticker).strip()]
        start_key = start_date.strftime("%Y-%m-%d")
        end_key = end_date.strftime("%Y-%m-%d")
        table = self._table()

        series_by_ticker = {}
        failed: List[str] = []

        for ticker in tickers_list:
            items = []
            kwargs = {
                "KeyConditionExpression": Key("ticker").eq(ticker)
                & Key("price_date").between(start_key, end_key)
            }

            while True:
                response = table.query(**kwargs)
                items.extend(response.get("Items", []))
                last_key = response.get("LastEvaluatedKey")
                if not last_key:
                    break
                kwargs["ExclusiveStartKey"] = last_key

            rows = []
            for item in items:
                close = _to_float(item.get("close"))
                price_date = item.get("price_date")
                if close is None or not price_date:
                    continue
                rows.append((pd.to_datetime(price_date), close))

            if not rows:
                failed.append(ticker)
                continue

            rows.sort(key=lambda row: row[0])
            series_by_ticker[ticker] = pd.Series(
                [close for _, close in rows],
                index=[date for date, _ in rows],
                name=ticker,
            )

        if not series_by_ticker:
            return pd.DataFrame(), failed

        return pd.concat(series_by_ticker.values(), axis=1), failed

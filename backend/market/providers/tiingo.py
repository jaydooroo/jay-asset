from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List, Tuple

import pandas as pd
import requests

from market.config import tiingo_api_key
from market.repository import PriceRepository


logger = logging.getLogger(__name__)


class TiingoPriceRepository(PriceRepository):
    """
    Historical daily close prices from Tiingo's EOD API.

    Tiingo authentication uses a token. Set:
      TIINGO_API_KEY=...
    """

    base_url = "https://api.tiingo.com/tiingo/daily"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or tiingo_api_key()
        if not self.api_key:
            raise RuntimeError("TIINGO_API_KEY is required when MARKET_INGEST_PROVIDER=tiingo")

    def get_close_prices(
        self,
        tickers: Iterable[str],
        start_date: datetime,
        end_date: datetime,
    ) -> Tuple[pd.DataFrame, List[str]]:
        session = requests.Session()
        session.headers.update(
            {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        series_by_ticker = {}
        failed: List[str] = []

        for ticker in [str(t).strip().upper() for t in tickers if str(t).strip()]:
            url = f"{self.base_url}/{ticker}/prices"
            params = {
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "format": "json",
            }

            try:
                response = session.get(url, params=params, timeout=20)
                response.raise_for_status()
                payload = response.json()
            except Exception as exc:
                logger.warning("Tiingo download failed for %s: %s", ticker, exc)
                failed.append(ticker)
                continue

            if not isinstance(payload, list) or not payload:
                logger.warning("Tiingo returned no price rows for %s", ticker)
                failed.append(ticker)
                continue

            rows = []
            for item in payload:
                if not isinstance(item, dict):
                    continue
                raw_date = item.get("date")
                close = item.get("adjClose", item.get("close"))
                if raw_date is None or close is None:
                    continue
                try:
                    rows.append((pd.to_datetime(raw_date).tz_localize(None).normalize(), float(close)))
                except Exception:
                    continue

            if not rows:
                logger.warning("Tiingo returned no usable close rows for %s", ticker)
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

"""Price fixtures shared by the tests: a fake repository and price builders."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

from market.repository import PriceRepository

REPO_DIR = Path(__file__).resolve().parents[2]

# Weekdays minus US federal holidays: about 250 sessions a year, like the
# real market. Plain weekdays (~261 a year) would hide date-window bugs that
# only appear when a year holds fewer trading days.
TRADING_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())


def trading_days(end, periods: int) -> pd.DatetimeIndex:
    return pd.date_range(end=pd.Timestamp(end).normalize(), periods=periods, freq=TRADING_DAY)


class FakePriceRepository(PriceRepository):
    """In-memory price store that slices by date like the DynamoDB repository."""

    def __init__(self, prices: pd.DataFrame):
        self.prices = prices.sort_index()
        self.calls = []

    def get_close_prices(self, tickers, start_date, end_date):
        tickers = [str(t).strip().upper() for t in tickers if str(t).strip()]
        self.calls.append((tickers, start_date, end_date))
        window = self.prices.loc[pd.Timestamp(start_date.date()) : pd.Timestamp(end_date.date())]
        present = [t for t in tickers if t in window.columns and window[t].notna().any()]
        failed = [t for t in tickers if t not in present]
        if not present:
            return pd.DataFrame(), failed
        return window[present].dropna(how="all"), failed


def make_prices(drifts: dict, days: int = 400, end=None, start_price: float = 100.0) -> pd.DataFrame:
    """
    Business-day close prices that grow by a constant daily return per ticker.

    A positive drift gives positive momentum on every lookback, a negative
    drift negative momentum, so the expected strategy decision is obvious.
    `end` defaults to today so strategies that read "the last N days" find data.
    """
    index = trading_days(end or datetime.today(), days)
    steps = np.arange(days)
    return pd.DataFrame(
        {ticker: start_price * (1.0 + drift) ** steps for ticker, drift in drifts.items()},
        index=index,
    )


def random_walk_prices(tickers, days: int = 400, seed: int = 0, end=None) -> pd.DataFrame:
    """Noisy prices for property tests (weights must stay valid whatever happens)."""
    rng = np.random.default_rng(seed)
    index = trading_days(end or datetime.today(), days)
    returns = rng.normal(0.0003, 0.012, size=(days, len(tickers)))
    return pd.DataFrame(100.0 * np.cumprod(1.0 + returns, axis=0), index=index, columns=list(tickers))

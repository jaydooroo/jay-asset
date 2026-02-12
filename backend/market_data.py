from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Tuple

import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr


def download_close_prices(
    tickers: Iterable[str],
    start_date: datetime,
    end_date: datetime,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Download daily close prices for tickers.

    Tries Stooq first (often more reliable in restricted environments), then
    falls back to a single Yahoo Finance batch download for missing tickers.

    Returns:
      - price_data: DataFrame indexed by date, columns are ticker symbols, values are closes
      - failed: list of tickers that could not be downloaded from either source
    """
    tickers_list = list(tickers)
    price_data, failed = _download_stooq(tickers_list, start_date, end_date)

    missing = [t for t in tickers_list if t not in price_data.columns]
    if missing:
        yahoo_price, yahoo_failed = _download_yahoo_batch(missing, start_date, end_date)
        failed.extend(yahoo_failed)
        if not yahoo_price.empty:
            price_data = pd.concat([price_data, yahoo_price], axis=1)

    return price_data, failed


def _download_stooq(
    tickers: List[str],
    start_date: datetime,
    end_date: datetime,
) -> Tuple[pd.DataFrame, List[str]]:
    # Stooq symbols for US ETFs typically use the ".US" suffix (e.g., SPY.US).
    series_by_ticker = {}
    failed: List[str] = []

    for ticker in tickers:
        symbol = ticker if "." in ticker else f"{ticker}.US"
        try:
            df = pdr.DataReader(symbol, "stooq", start=start_date, end=end_date)
        except Exception:
            failed.append(ticker)
            continue

        if df is None or df.empty or "Close" not in df.columns:
            failed.append(ticker)
            continue

        df = df.sort_index()
        series_by_ticker[ticker] = df["Close"].rename(ticker)

    if not series_by_ticker:
        return pd.DataFrame(), failed

    return pd.concat(series_by_ticker.values(), axis=1), failed


def _download_yahoo_batch(
    tickers: List[str],
    start_date: datetime,
    end_date: datetime,
) -> Tuple[pd.DataFrame, List[str]]:
    # Yahoo download in one request reduces the chance of partial failures and is faster.
    failed: List[str] = []

    batch_data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        progress=False,
        threads=True,
        ignore_tz=True,
    )

    if batch_data is None or batch_data.empty:
        return pd.DataFrame(), tickers

    if isinstance(batch_data.columns, pd.MultiIndex):
        if "Close" not in batch_data.columns.levels[0]:
            return pd.DataFrame(), tickers
        price_data = batch_data["Close"]
    else:
        if "Close" in batch_data.columns:
            price_data = batch_data[["Close"]]
            price_data.columns = [tickers[0]]
        else:
            price_data = batch_data

    for ticker in tickers:
        if ticker not in price_data.columns:
            failed.append(ticker)

    return price_data, failed

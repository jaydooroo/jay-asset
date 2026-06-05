from __future__ import annotations

import logging
from io import StringIO
from datetime import datetime
from typing import Iterable, List, Tuple

import pandas as pd
import requests
import yfinance as yf
from pandas_datareader import data as pdr


logger = logging.getLogger(__name__)


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
    price_data, _stooq_direct_failed = _download_stooq_direct(tickers_list, start_date, end_date)

    missing = [t for t in tickers_list if t not in price_data.columns]
    if missing:
        stooq_reader_price, _stooq_reader_failed = _download_stooq_reader(missing, start_date, end_date)
        if not stooq_reader_price.empty:
            price_data = pd.concat([price_data, stooq_reader_price], axis=1)

    missing = [t for t in tickers_list if t not in price_data.columns]
    if missing:
        yahoo_price, _yahoo_failed = _download_yahoo_batch(missing, start_date, end_date)
        if not yahoo_price.empty:
            price_data = pd.concat([price_data, yahoo_price], axis=1)

    # Final failed tickers must be derived from merged data, not provider-local
    # failure lists (a ticker can fail Stooq but succeed on Yahoo fallback).
    final_failed = [t for t in tickers_list if t not in price_data.columns]
    return price_data, final_failed


def _stooq_symbol(ticker: str) -> str:
    return ticker if "." in ticker else f"{ticker}.US"


def _download_stooq_direct(
    tickers: List[str],
    start_date: datetime,
    end_date: datetime,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Download Stooq daily CSV directly.

    pandas_datareader also uses Stooq, but when Stooq returns an unexpected
    response the parser error can be opaque. This direct path gives us tighter
    validation and a clear fallback before Yahoo.
    """
    series_by_ticker = {}
    failed: List[str] = []

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }
    )

    for ticker in tickers:
        symbol = _stooq_symbol(ticker).lower()
        params = {
            "s": symbol,
            "d1": start_date.strftime("%Y%m%d"),
            "d2": end_date.strftime("%Y%m%d"),
            "i": "d",
        }
        try:
            response = session.get("https://stooq.com/q/d/l/", params=params, timeout=15)
            response.raise_for_status()
        except Exception as exc:
            logger.warning("Stooq direct download failed for %s (%s): %s", ticker, symbol, exc)
            failed.append(ticker)
            continue

        text = (response.text or "").strip()
        if not text or "Date" not in text.splitlines()[0]:
            preview = text[:120].replace("\n", " ")
            logger.warning("Stooq direct returned non-CSV data for %s (%s): %s", ticker, symbol, preview)
            failed.append(ticker)
            continue

        try:
            df = pd.read_csv(StringIO(text))
        except Exception as exc:
            logger.warning("Stooq direct CSV parse failed for %s (%s): %s", ticker, symbol, exc)
            failed.append(ticker)
            continue

        if df is None or df.empty or "Date" not in df.columns or "Close" not in df.columns:
            logger.warning("Stooq direct returned no usable close data for %s (%s)", ticker, symbol)
            failed.append(ticker)
            continue

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["Date", "Close"]).sort_values("Date")
        if df.empty:
            logger.warning("Stooq direct returned only invalid rows for %s (%s)", ticker, symbol)
            failed.append(ticker)
            continue

        series_by_ticker[ticker] = pd.Series(df["Close"].values, index=df["Date"], name=ticker)

    if not series_by_ticker:
        return pd.DataFrame(), failed

    return pd.concat(series_by_ticker.values(), axis=1), failed


def _download_stooq_reader(
    tickers: List[str],
    start_date: datetime,
    end_date: datetime,
) -> Tuple[pd.DataFrame, List[str]]:
    # Stooq symbols for US ETFs typically use the ".US" suffix (e.g., SPY.US).
    series_by_ticker = {}
    failed: List[str] = []

    for ticker in tickers:
        symbol = _stooq_symbol(ticker)
        try:
            df = pdr.DataReader(symbol, "stooq", start=start_date, end=end_date)
        except Exception as exc:
            logger.warning("Stooq download failed for %s (%s): %s", ticker, symbol, exc)
            failed.append(ticker)
            continue

        if df is None or df.empty or "Close" not in df.columns:
            logger.warning("Stooq returned no usable close data for %s (%s)", ticker, symbol)
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

    try:
        batch_data = yf.download(
            tickers,
            start=start_date,
            end=end_date,
            progress=False,
            threads=True,
            ignore_tz=True,
        )
    except Exception as exc:
        logger.warning("Yahoo Finance batch download failed for %s: %s", ",".join(tickers), exc)
        return pd.DataFrame(), tickers

    if batch_data is None or batch_data.empty:
        logger.warning("Yahoo Finance returned an empty dataset for %s", ",".join(tickers))
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
            logger.warning("Yahoo Finance did not return close data for %s", ticker)
            failed.append(ticker)

    return price_data, failed

import math
from datetime import datetime, timedelta

from market_data import download_close_prices

from .config import performance_lookback_days

# NOTE:
# This module is retained as a legacy fixed-weight snapshot helper.
# The scheduled performance pipeline now uses monthly walk-forward logic
# implemented in `performance/backtest.py`.


def _clean_weights(weights: dict) -> dict:
    cleaned = {}
    for ticker, weight in (weights or {}).items():
        try:
            value = float(weight)
        except Exception:
            continue
        if value <= 0:
            continue
        cleaned[str(ticker)] = value
    total = sum(cleaned.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in cleaned.items()}


def _max_drawdown(value_series):
    running_max = value_series.cummax()
    drawdowns = (value_series / running_max) - 1.0
    return float(drawdowns.min()) if len(drawdowns) else 0.0


def snapshot_metrics_from_weights(weights: dict) -> dict:
    """
    Compute 1Y snapshot performance metrics from fixed portfolio weights.
    """
    normalized = _clean_weights(weights)
    if not normalized:
        return {"error": "No valid positive allocation weights"}

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=performance_lookback_days() + 10)
    tickers = list(normalized.keys())

    price_data, failed = download_close_prices(tickers, start_date, end_date)
    if price_data is None or price_data.empty:
        return {"error": "No price data available", "missing_tickers": failed}

    price_data = price_data.sort_index().ffill().dropna(axis=1, how="all")
    available = [ticker for ticker in tickers if ticker in price_data.columns]
    if not available:
        return {"error": "No valid tickers available for performance", "missing_tickers": failed}

    effective_weights = _clean_weights({ticker: normalized[ticker] for ticker in available})
    if not effective_weights:
        return {"error": "Unable to normalize available weights", "missing_tickers": failed}

    aligned = price_data[available].dropna(how="all").ffill().dropna()
    if aligned.empty or len(aligned) < 2:
        return {"error": "Insufficient historical data", "missing_tickers": failed}

    base = aligned.iloc[0]
    rel = aligned.divide(base)
    portfolio = sum(rel[ticker] * weight for ticker, weight in effective_weights.items())
    portfolio = portfolio.dropna()

    if len(portfolio) < 2:
        return {"error": "Insufficient portfolio history", "missing_tickers": failed}

    returns = portfolio.pct_change().dropna()
    cumulative_return = float((portfolio.iloc[-1] / portfolio.iloc[0]) - 1.0)
    n_days = max(len(returns), 1)
    cagr = float((1.0 + cumulative_return) ** (252.0 / n_days) - 1.0)
    volatility = float(returns.std() * math.sqrt(252.0)) if len(returns) else 0.0
    max_dd = _max_drawdown(portfolio)

    return {
        "as_of": aligned.index[-1].strftime("%Y-%m-%d"),
        "num_points": int(len(portfolio)),
        "lookback_days": int((aligned.index[-1] - aligned.index[0]).days),
        "cumulative_return_1y": round(cumulative_return, 6),
        "cagr_1y": round(cagr, 6),
        "max_drawdown_1y": round(max_dd, 6),
        "volatility_annual": round(volatility, 6),
        "weights_used": {ticker: round(weight, 6) for ticker, weight in effective_weights.items()},
        "missing_tickers": sorted(set(failed)),
    }

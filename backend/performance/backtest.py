from __future__ import annotations

import math
from datetime import datetime, timedelta

import pandas as pd

from market_data import download_close_prices

from .config import performance_backtest_months, performance_lookback_days


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
    return {ticker: value / total for ticker, value in cleaned.items()}


def _max_drawdown(equity_curve: pd.Series) -> float:
    if equity_curve is None or equity_curve.empty:
        return 0.0
    running_max = equity_curve.cummax()
    drawdowns = (equity_curve / running_max) - 1.0
    return float(drawdowns.min()) if len(drawdowns) else 0.0


def _monthly_prices(prices: pd.DataFrame) -> pd.DataFrame:
    # Month-end sampled prices (last available trading day in each month).
    return prices.resample("ME").last().dropna(how="all")


def run_monthly_walkforward_backtest(spec, parameters: dict | None = None) -> dict:
    """
    Shared monthly walk-forward backtest engine.

    For each monthly rebalance date:
    - Use history up to that date to compute weights
    - Apply weights over the next monthly period
    """
    params = spec.normalize_parameters(parameters or spec.default_parameters())
    universe = spec.universe(params)
    if not universe:
        return {"error": "Strategy universe is empty"}

    months = max(1, int(performance_backtest_months()))
    min_lookback_days = max(int(spec.min_lookback_days), int(performance_lookback_days()))
    fetch_days = min_lookback_days + (months + 2) * 31 + 45

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=fetch_days)
    prices, failed = download_close_prices(universe, start_date, end_date)
    if prices is None or prices.empty:
        return {"error": "No price data available", "missing_tickers": sorted(set(failed))}

    prices = prices.sort_index().ffill().dropna(axis=1, how="all")
    available = [ticker for ticker in universe if ticker in prices.columns]
    missing = sorted(set(failed + [ticker for ticker in universe if ticker not in available]))
    if not available:
        return {"error": "No valid tickers available for backtest", "missing_tickers": missing}

    prices = prices[available].dropna(how="all").ffill().dropna(how="all")
    monthly = _monthly_prices(prices)
    if len(monthly) < months + 2:
        return {
            "error": f"Insufficient monthly history: need at least {months + 2} monthly points, got {len(monthly)}",
            "missing_tickers": missing,
        }

    eligible_rebalance = []
    for date in monthly.index:
        history = prices.loc[:date]
        if len(history) >= min_lookback_days:
            eligible_rebalance.append(date)

    if len(eligible_rebalance) < months + 1:
        return {
            "error": (
                f"Insufficient lookback-qualified rebalance points: need {months + 1}, got {len(eligible_rebalance)}. "
                "Try PERFORMANCE_LOOKBACK_DAYS=252 or reduce PERFORMANCE_BACKTEST_MONTHS."
            ),
            "missing_tickers": missing,
        }

    rebalance_points = eligible_rebalance[-(months + 1) :]
    period_returns = []
    period_details = []

    for i in range(len(rebalance_points) - 1):
        as_of = rebalance_points[i]
        next_as_of = rebalance_points[i + 1]

        history = prices.loc[:as_of]
        decision = spec.compute_weights(history, params)
        if not isinstance(decision, dict):
            return {"error": f"{spec.strategy_id} decision is invalid at {as_of.date()}", "missing_tickers": missing}
        if "error" in decision:
            return {
                "error": f"{spec.strategy_id} failed at {as_of.date()}: {decision['error']}",
                "missing_tickers": missing,
            }

        raw_weights = _clean_weights(decision.get("allocation_weights"))
        if not raw_weights:
            return {
                "error": f"{spec.strategy_id} returned empty/invalid weights at {as_of.date()}",
                "missing_tickers": missing,
            }

        start_prices = monthly.loc[as_of]
        end_prices = monthly.loc[next_as_of]
        valid_tickers = []
        for ticker in raw_weights.keys():
            if ticker not in monthly.columns:
                continue
            start_price = start_prices.get(ticker)
            end_price = end_prices.get(ticker)
            if pd.isna(start_price) or pd.isna(end_price) or float(start_price) <= 0:
                continue
            valid_tickers.append(ticker)

        if not valid_tickers:
            return {
                "error": f"No valid price path for weighted assets at {as_of.date()}",
                "missing_tickers": missing,
            }

        normalized = _clean_weights({ticker: raw_weights[ticker] for ticker in valid_tickers})
        period_return = 0.0
        for ticker, weight in normalized.items():
            ticker_return = float(end_prices[ticker] / start_prices[ticker] - 1.0)
            period_return += weight * ticker_return

        period_returns.append(float(period_return))
        period_details.append(
            {
                "as_of": as_of.strftime("%Y-%m-%d"),
                "next_as_of": next_as_of.strftime("%Y-%m-%d"),
                "period_return": round(float(period_return), 6),
                "weights": {ticker: round(float(weight), 6) for ticker, weight in normalized.items()},
            }
        )

    if not period_returns:
        return {"error": "No backtest periods were produced", "missing_tickers": missing}

    equity_points = [1.0]
    for value in period_returns:
        equity_points.append(equity_points[-1] * (1.0 + value))

    equity_index = [point.strftime("%Y-%m-%d") for point in rebalance_points]
    equity_series = pd.Series(equity_points, index=equity_index)
    monthly_returns = pd.Series(period_returns, index=[point.strftime("%Y-%m-%d") for point in rebalance_points[1:]])

    total_return = float(equity_series.iloc[-1] - 1.0)
    n_months = len(period_returns)
    cagr = float((1.0 + total_return) ** (12.0 / float(n_months)) - 1.0)
    if len(monthly_returns) > 1:
        volatility = float(monthly_returns.std(ddof=1) * math.sqrt(12.0))
    else:
        volatility = 0.0
    max_dd = _max_drawdown(equity_series)

    win_rate = float((monthly_returns > 0).sum() / len(monthly_returns))
    best_month = float(monthly_returns.max())
    worst_month = float(monthly_returns.min())

    metrics = {
        "as_of": equity_index[-1],
        "window_start": equity_index[0],
        "months_tested": int(n_months),
        "lookback_min_days": int(min_lookback_days),
        "cumulative_return_period": round(total_return, 6),
        "cagr_annualized": round(cagr, 6),
        "max_drawdown_period": round(max_dd, 6),
        "volatility_annualized": round(volatility, 6),
        "win_rate_monthly": round(win_rate, 6),
        "best_month_return": round(best_month, 6),
        "worst_month_return": round(worst_month, 6),
        "rebalance_frequency": spec.rebalance_frequency,
        "strategy_version": spec.strategy_version,
        "missing_tickers": missing,
        "monthly_returns": [
            {"period_end": index, "return": round(float(value), 6)} for index, value in monthly_returns.items()
        ],
    }

    # Backward-compatible aliases for existing frontend naming expectations.
    if n_months == 12:
        metrics["cumulative_return_1y"] = metrics["cumulative_return_period"]
        metrics["cagr_1y"] = metrics["cagr_annualized"]
        metrics["max_drawdown_1y"] = metrics["max_drawdown_period"]
        metrics["volatility_annual"] = metrics["volatility_annualized"]

    return {"metrics": metrics, "parameters": params}

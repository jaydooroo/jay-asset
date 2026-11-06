"""
Research backtest: every strategy alone and in mixes, over long history.

Kept apart from the service. Prices are Tiingo dividend-adjusted closes
cached as CSV under <repo>/.research/ (outside backend/, so `sam build`
never packages them), not DynamoDB. Nothing in the app imports this module.

    cd backend
    python -m research.mix_backtest              # uses the cache, downloads if missing
    python -m research.mix_backtest --refresh    # download again from Tiingo
    python -m research.mix_backtest --cost 0.002

Simulation rules (stricter than performance/backtest.py):
  - Decide at each month-end close from history up to that close, using each
    spec's compute_weights, so the rules match the service exactly.
  - Trade at the next trading day's close.
  - Pay `cost` on traded value (sum of |weight change|) at every rebalance.
  - Between rebalances weights drift with prices.

Mixes blend the strategies' target weights into one portfolio per month.
"Past best" picks its combo each December from returns known at that time;
"Hindsight best" picks from the full period and is shown only as the
overfitting reference it would be if chosen that way.
"""
from __future__ import annotations

import argparse
import itertools
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from performance.specs import SPECS
from strategies.static_allocation import STATIC_PORTFOLIOS

RESEARCH_DIR = Path(__file__).resolve().parents[2] / ".research"
PRICE_CACHE = RESEARCH_DIR / "tiingo_adjclose.csv"
OUTPUT_DIR = RESEARCH_DIR / "output"

LOOKBACK_DAYS = 260  # longest spec lookback (252 trading days) plus a margin
CASH = "BIL"
CRISIS_YEARS = (2008, 2020, 2022)

STRATEGY_IDS = list(SPECS)
TACTICAL_IDS = [sid for sid in STRATEGY_IDS if sid not in STATIC_PORTFOLIOS]


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------

def strategy_universe() -> list[str]:
    tickers: set[str] = {CASH}
    for spec in SPECS.values():
        tickers.update(spec.universe(spec.default_parameters()))
    return sorted(tickers)


def load_prices(tickers: list[str], start: str, refresh: bool) -> pd.DataFrame:
    if PRICE_CACHE.exists() and not refresh:
        cached = pd.read_csv(PRICE_CACHE, index_col=0, parse_dates=True)
        missing = [t for t in tickers if t not in cached.columns]
        if not missing:
            print(f"Using cached prices: {PRICE_CACHE}")
            return cached[tickers]
        print(f"Cache lacks {missing}; downloading again.")

    from market.providers import TiingoPriceRepository  # needs TIINGO_API_KEY

    print(f"Downloading {len(tickers)} tickers from Tiingo since {start} ...")
    prices, failed = TiingoPriceRepository().get_close_prices(
        tickers, datetime.fromisoformat(start), datetime.today()
    )
    if failed:
        raise SystemExit(f"Tiingo download failed for: {failed}")
    RESEARCH_DIR.mkdir(exist_ok=True)
    prices = prices.sort_index()[tickers]
    prices.to_csv(PRICE_CACHE)
    print(f"Saved {PRICE_CACHE}")
    return prices


def decision_dates(prices: pd.DataFrame) -> list[pd.Timestamp]:
    """Month-end trading days with full lookback that have a next trading day."""
    month_ends = prices.groupby(prices.index.to_period("M")).tail(1).index
    first_ok = prices.index[LOOKBACK_DAYS]
    return [d for d in month_ends if first_ok <= d < prices.index[-1]]


# ----------------------------------------------------------------------------
# Targets and simulation
# ----------------------------------------------------------------------------

def _clean(weights: dict) -> dict[str, float]:
    w = {str(k): float(v) for k, v in (weights or {}).items() if float(v) > 0}
    total = sum(w.values())
    return {k: v / total for k, v in w.items()}


def strategy_targets(prices: pd.DataFrame, dates: list[pd.Timestamp]) -> dict[str, dict]:
    """{strategy_id: {decision_date: weights}} from each spec's compute_weights."""
    params = {sid: spec.normalize_parameters(spec.default_parameters()) for sid, spec in SPECS.items()}
    targets: dict[str, dict] = {sid: {} for sid in STRATEGY_IDS}
    for i, d in enumerate(dates):
        history = prices.loc[:d]
        for sid, spec in SPECS.items():
            out = spec.compute_weights(history, params[sid])
            if "error" in out:
                raise RuntimeError(f"{sid} failed at {d.date()}: {out['error']}")
            targets[sid][d] = _clean(out["allocation_weights"])
        if (i + 1) % 24 == 0:
            print(f"  targets computed through {d.date()}")
    return targets


def blend(targets: dict[str, dict], mix: dict[str, float], d: pd.Timestamp) -> dict[str, float]:
    out: dict[str, float] = {}
    for sid, m in mix.items():
        for ticker, w in targets[sid][d].items():
            out[ticker] = out.get(ticker, 0.0) + m * w
    return out


def simulate(prices: pd.DataFrame, schedule: dict[pd.Timestamp, dict], cost: float):
    """
    Daily simulation of a monthly target schedule.

    Returns (daily_returns, turnovers) where turnover is the traded value as a
    fraction of the portfolio (sum of |weight change|) at each rebalance.
    """
    tickers = list(prices.columns)
    col = {t: i for i, t in enumerate(tickers)}
    rets = prices.pct_change().fillna(0.0).to_numpy()
    index = prices.index
    position = {d: index.get_loc(d) + 1 for d in schedule}  # trade next trading day
    trades = {position[d]: schedule[d] for d in schedule}

    start = min(trades)
    w = np.zeros(len(tickers))
    daily, turnovers = [], []
    for i in range(start, len(index)):
        r = float(w @ rets[i])
        if w.any():
            w = w * (1.0 + rets[i]) / (1.0 + r)
        if i in trades:
            target = np.zeros(len(tickers))
            for t, x in trades[i].items():
                target[col[t]] = x
            turnover = float(np.abs(target - w).sum())
            r = (1.0 + r) * (1.0 - cost * turnover) - 1.0
            w = target
            turnovers.append(turnover)
        daily.append(r)
    return pd.Series(daily, index=index[start:]), turnovers


def monthly(daily: pd.Series) -> pd.Series:
    return (1.0 + daily).resample("ME").prod() - 1.0


# ----------------------------------------------------------------------------
# Mix rules (each uses only information available at the decision date)
# ----------------------------------------------------------------------------

def sharpe(monthly_returns: pd.Series, cash_monthly: pd.Series) -> float:
    excess = (monthly_returns - cash_monthly.reindex(monthly_returns.index).fillna(0.0)).dropna()
    if len(excess) < 2 or excess.std() == 0:
        return float("nan")
    return float(excess.mean() / excess.std() * math.sqrt(12))


def equal(ids) -> dict[str, float]:
    return {sid: 1.0 / len(ids) for sid in ids}


def inverse_vol_mix(alone_monthly: pd.DataFrame, ids, d) -> dict[str, float]:
    past = alone_monthly.loc[: d, ids].tail(12)
    if len(past) < 12:
        return equal(ids)
    inv = 1.0 / past.std().replace(0, np.nan)
    inv = inv.fillna(inv.max())
    return (inv / inv.sum()).to_dict()


def low_corr_combo(alone_monthly: pd.DataFrame, ids, d, size: int = 3):
    past = alone_monthly.loc[: d, ids].tail(36)
    if len(past) < 24:
        return None
    corr = past.corr()
    best, best_score = None, float("inf")
    for combo in itertools.combinations(ids, size):
        score = np.mean([corr.loc[a, b] for a, b in itertools.combinations(combo, 2)])
        if score < best_score:
            best, best_score = combo, score
    return best


def best_sharpe_combo(alone_monthly: pd.DataFrame, cash_monthly: pd.Series, ids, d=None):
    """Equal-weight combo of 2-4 strategies with the best Sharpe up to `d` (all data if None)."""
    past = alone_monthly.loc[:d, ids] if d is not None else alone_monthly[ids]
    if len(past) < 24:
        return None
    best, best_score = None, float("-inf")
    for size in (2, 3, 4):
        for combo in itertools.combinations(ids, size):
            score = sharpe(past[list(combo)].mean(axis=1), cash_monthly)
            if score > best_score:
                best, best_score = combo, score
    return best


def yearly_schedule(dates, pick, fallback):
    """Re-pick at each December decision (applies to the next year); hold otherwise."""
    mixes, selections, current = {}, [], None
    for d in dates:
        if current is None or d.month == 12:
            combo = pick(d)
            chosen = equal(combo) if combo else fallback
            if chosen != current:
                selections.append((d, "+".join(combo) if combo else "fallback: equal weight"))
            current = chosen
        mixes[d] = current
    return mixes, selections


# ----------------------------------------------------------------------------
# Metrics and report
# ----------------------------------------------------------------------------

def metrics(daily: pd.Series, turnovers: list[float], cash_monthly: pd.Series) -> dict:
    equity = (1.0 + daily).cumprod()
    years = (daily.index[-1] - daily.index[0]).days / 365.25
    m = monthly(daily)
    yearly = (1.0 + daily).resample("YE").prod() - 1.0
    first_full, last_full = daily.index[0].year + 1, daily.index[-1].year - 1
    full_years = yearly[(yearly.index.year >= first_full) & (yearly.index.year <= last_full)]
    row = {
        "CAGR": equity.iloc[-1] ** (1.0 / years) - 1.0,
        "Vol": m.std() * math.sqrt(12),
        "Sharpe": sharpe(m, cash_monthly),
        "MaxDD": float((equity / equity.cummax() - 1.0).min()),
        "WorstYear": float(full_years.min()),
        # One-way turnover per year, excluding the initial purchase.
        "Turnover/yr": sum(turnovers[1:]) / 2.0 / years,
    }
    for y in CRISIS_YEARS:
        hit = yearly[yearly.index.year == y]
        row[str(y)] = float(hit.iloc[0]) if len(hit) else float("nan")
    return row


def fmt_table(df: pd.DataFrame) -> str:
    pct = [c for c in df.columns if c not in ("Sharpe", "Turnover/yr")]
    out = df.copy()
    for c in pct:
        out[c] = out[c].map(lambda v: f"{v * 100:6.1f}%")
    out["Sharpe"] = out["Sharpe"].map(lambda v: f"{v:5.2f}")
    out["Turnover/yr"] = out["Turnover/yr"].map(lambda v: f"{v * 100:5.0f}%")
    return out.to_string()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", default="2007-01-01", help="download start date (default 2007-01-01)")
    parser.add_argument("--cost", type=float, default=0.001, help="cost per unit of traded value (default 0.001)")
    parser.add_argument("--refresh", action="store_true", help="download prices again instead of using the cache")
    args = parser.parse_args()

    tickers = strategy_universe()
    prices = load_prices(tickers, args.start, args.refresh)

    # Start where every ticker trades, so all strategies see the same period.
    listed = {t: prices[t].first_valid_index() for t in tickers}
    common_start = max(listed.values())
    latest = sorted(t for t, d in listed.items() if d == common_start)
    prices = prices.loc[common_start:].ffill()
    dates = decision_dates(prices)
    print(f"Common start {common_start.date()} (latest data: {', '.join(latest)}); "
          f"{len(dates)} monthly decisions {dates[0].date()} .. {dates[-1].date()}")

    print("Computing strategy targets ...")
    targets = strategy_targets(prices, dates)

    cash_daily = prices[CASH].pct_change().fillna(0.0)
    cash_monthly = monthly(cash_daily)

    results, rows = {}, {}

    def run(name, schedule):
        daily, turnovers = simulate(prices, schedule, args.cost)
        results[name] = daily
        rows[name] = metrics(daily, turnovers, cash_monthly)

    for sid in STRATEGY_IDS:
        run(f"alone: {sid}", {d: targets[sid][d] for d in dates})

    # Monthly rows are labelled by calendar month end, so the `.loc[:d]` in each
    # mix rule only sees months that finished on or before decision date d.
    alone_monthly = pd.DataFrame({sid: monthly(results[f"alone: {sid}"]) for sid in STRATEGY_IDS})

    run(f"equal: tactical {len(TACTICAL_IDS)}", {d: blend(targets, equal(TACTICAL_IDS), d) for d in dates})
    run(f"equal: all {len(STRATEGY_IDS)}", {d: blend(targets, equal(STRATEGY_IDS), d) for d in dates})
    run("inverse vol: tactical",
        {d: blend(targets, inverse_vol_mix(alone_monthly, TACTICAL_IDS, d), d) for d in dates})

    low_mix, low_sel = yearly_schedule(dates, lambda d: low_corr_combo(alone_monthly, TACTICAL_IDS, d),
                                       equal(TACTICAL_IDS))
    run("low corr: 3 tactical", {d: blend(targets, low_mix[d], d) for d in dates})

    past_mix, past_sel = yearly_schedule(
        dates, lambda d: best_sharpe_combo(alone_monthly, cash_monthly, STRATEGY_IDS, d), equal(STRATEGY_IDS)
    )
    run("past best: 2-4 (yearly)", {d: blend(targets, past_mix[d], d) for d in dates})

    hindsight = best_sharpe_combo(alone_monthly, cash_monthly, STRATEGY_IDS)
    run(f"HINDSIGHT best: {'+'.join(hindsight)}", {d: blend(targets, equal(hindsight), d) for d in dates})

    summary = pd.DataFrame(rows).T
    corr = alone_monthly.corr()

    first, last = results[f"alone: {STRATEGY_IDS[0]}"].index[[0, -1]]
    print(f"\nPeriod {first.date()} .. {last.date()}, next-day execution, cost {args.cost:.2%} of traded value")
    print(f"({CRISIS_YEARS[0]} covers only part of the year: the test starts {first.date()}.)\n")
    print(fmt_table(summary))
    print("\nMonthly return correlation between strategies (standalone):\n")
    print(corr.round(2).to_string())
    print("\nLow-correlation picks (set each December):")
    for d, s in low_sel:
        print(f"  {d.date()}  {s}")
    print("\nPast-best picks (set each December from data known then):")
    for d, s in past_sel:
        print(f"  {d.date()}  {s}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_DIR / "summary.csv")
    corr.to_csv(OUTPUT_DIR / "correlation.csv")
    pd.DataFrame({k: monthly(v) for k, v in results.items()}).to_csv(OUTPUT_DIR / "monthly_returns.csv")
    pd.DataFrame(
        [("low corr", d.date(), s) for d, s in low_sel] + [("past best", d.date(), s) for d, s in past_sel],
        columns=["rule", "decided_on", "combo"],
    ).to_csv(OUTPUT_DIR / "selections.csv", index=False)
    print(f"\nCSV files written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

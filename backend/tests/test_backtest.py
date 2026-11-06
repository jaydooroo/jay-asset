"""Monthly walk-forward backtest engine (performance/backtest.py) and its runner."""
from datetime import datetime

import pandas as pd
import pytest

from helpers import make_prices, random_walk_prices
from performance import backtest, runner
from performance.backtest import _clean_weights, _max_drawdown, _monthly_prices, run_monthly_walkforward_backtest
from performance.specs import SPECS
from performance.specs.base import StrategyPerformanceSpec

TODAY = datetime(2026, 10, 15)


@pytest.fixture
def clock(monkeypatch):
    """Pin the backtest's "now": `clock(datetime(...))`."""

    def set_now(now):
        monkeypatch.setattr(backtest, "_utcnow", lambda: now)

    set_now(TODAY)
    return set_now


class FixedWeightsSpec(StrategyPerformanceSpec):
    """Test spec that holds given weights and records every history it sees."""

    def __init__(self, weights, min_lookback_days=21):
        super().__init__(strategy_id="fixed", strategy_name="Fixed", min_lookback_days=min_lookback_days)
        object.__setattr__(self, "weights", weights)
        object.__setattr__(self, "seen", [])

    def default_parameters(self):
        return {}

    def universe(self, parameters):
        return sorted(self.weights)

    def compute_weights(self, history, parameters):
        self.seen.append(history.index[-1])
        return {"allocation_weights": dict(self.weights)}


def month_end_prices(prices, now=TODAY):
    month_ends = prices.groupby(prices.index.to_period("M")).tail(1)
    return month_ends[month_ends.index.to_period("M") < pd.Timestamp(now).to_period("M")]


# --- Helpers ----------------------------------------------------------------

def test_clean_weights_drops_bad_entries_and_normalizes():
    assert _clean_weights({"SPY": 3, "AGG": "1", "X": 0, "Y": -1, "Z": "abc"}) == {"SPY": 0.75, "AGG": 0.25}
    assert _clean_weights({}) == {}
    assert _clean_weights(None) == {}


def test_max_drawdown_is_the_worst_peak_to_trough_fall():
    assert _max_drawdown(pd.Series([1.0, 1.2, 0.9, 1.1, 1.3, 1.04])) == pytest.approx(-0.25)
    assert _max_drawdown(pd.Series([1.0, 1.1, 1.2])) == 0.0
    assert _max_drawdown(pd.Series(dtype=float)) == 0.0


def test_monthly_prices_use_real_trading_days_and_skip_the_current_month(clock):
    prices = make_prices({"SPY": 0.001}, days=60, end="2026-10-14")
    monthly = _monthly_prices(prices)
    assert list(monthly.index.strftime("%Y-%m-%d")) == ["2026-07-31", "2026-08-31", "2026-09-30"]


# --- Engine -----------------------------------------------------------------

def test_buy_and_hold_matches_the_price_change(use_prices, clock):
    prices = make_prices({"SPY": 0.0007}, days=800, end=TODAY)
    use_prices(prices)

    metrics = run_monthly_walkforward_backtest(FixedWeightsSpec({"SPY": 1.0}))["metrics"]

    month_ends = month_end_prices(prices)["SPY"]
    assert metrics["months_tested"] == 12
    assert metrics["as_of"] == "2026-09-30"
    assert metrics["window_start"] == month_ends.index[-13].strftime("%Y-%m-%d")
    assert metrics["cumulative_return_period"] == pytest.approx(month_ends.iloc[-1] / month_ends.iloc[-13] - 1, abs=1e-6)
    assert metrics["max_drawdown_period"] == 0.0
    assert metrics["win_rate_monthly"] == 1.0
    assert len(metrics["monthly_returns"]) == 12


def test_mixed_portfolio_rebalances_back_to_target_every_month(use_prices, clock):
    prices = random_walk_prices(["SPY", "AGG"], days=800, seed=3, end=TODAY)
    use_prices(prices)

    metrics = run_monthly_walkforward_backtest(FixedWeightsSpec({"SPY": 0.6, "AGG": 0.4}))["metrics"]

    monthly = month_end_prices(prices).iloc[-13:]
    returns = monthly.pct_change().dropna()
    expected = 0.6 * returns["SPY"] + 0.4 * returns["AGG"]
    assert [m["return"] for m in metrics["monthly_returns"]] == pytest.approx(list(expected), abs=1e-6)
    assert metrics["cumulative_return_period"] == pytest.approx((1 + expected).prod() - 1, abs=1e-5)
    assert metrics["worst_month_return"] == pytest.approx(expected.min(), abs=1e-6)


def test_decisions_only_see_history_up_to_the_rebalance_date(use_prices, clock):
    use_prices(make_prices({"SPY": 0.001}, days=800, end=TODAY))
    spec = FixedWeightsSpec({"SPY": 1.0})

    metrics = run_monthly_walkforward_backtest(spec)["metrics"]

    decided_at = [d.strftime("%Y-%m-%d") for d in spec.seen]
    assert decided_at == [metrics["window_start"]] + [m["period_end"] for m in metrics["monthly_returns"][:-1]]


def test_weights_of_assets_without_prices_go_to_the_rest(use_prices, clock):
    use_prices(make_prices({"SPY": 0.001}, days=800, end=TODAY))
    result = run_monthly_walkforward_backtest(FixedWeightsSpec({"SPY": 0.5, "GONE": 0.5}))
    assert result["metrics"]["missing_tickers"] == ["GONE"]
    assert result["metrics"]["win_rate_monthly"] == 1.0


def test_backtest_months_setting(use_prices, clock, monkeypatch):
    monkeypatch.setenv("PERFORMANCE_BACKTEST_MONTHS", "6")
    use_prices(make_prices({"SPY": 0.001}, days=800, end=TODAY))
    metrics = run_monthly_walkforward_backtest(FixedWeightsSpec({"SPY": 1.0}))["metrics"]
    assert metrics["months_tested"] == 6
    assert "cagr_1y" not in metrics  # 1y aliases only exist for 12-month runs


def test_strategy_error_names_the_strategy_and_date(use_prices, clock):
    class Broken(FixedWeightsSpec):
        def compute_weights(self, history, parameters):
            return {"error": "boom"}

    use_prices(make_prices({"SPY": 0.001}, days=800, end=TODAY))
    error = run_monthly_walkforward_backtest(Broken({"SPY": 1.0}))["error"]
    assert error.startswith("fixed failed at ") and error.endswith("boom")


def test_too_little_history_is_an_error(use_prices, clock):
    use_prices(make_prices({"SPY": 0.001}, days=200, end=TODAY))
    assert "Insufficient" in run_monthly_walkforward_backtest(FixedWeightsSpec({"SPY": 1.0}))["error"]


def test_no_stored_prices_is_an_error(use_prices, clock):
    use_prices(make_prices({"OTHER": 0.001}, days=800, end=TODAY))
    result = run_monthly_walkforward_backtest(FixedWeightsSpec({"SPY": 1.0}))
    assert result["error"] == "No price data available"
    assert result["missing_tickers"] == ["SPY"]


# --- Every real strategy on any day of the month ---------------------------

ALL_TICKERS = sorted({t for spec in SPECS.values() for t in spec.universe(spec.default_parameters())})


@pytest.mark.parametrize("day", [1, 2, 15, 27, 28, 29, 30, 31])
@pytest.mark.parametrize("strategy_id", sorted(SPECS))
def test_every_strategy_backtests_on_any_day_of_the_month(use_prices, clock, strategy_id, day):
    """
    Regression: runs late in the month used to fail for 252-day strategies
    because the download window counted trading days as calendar days.
    The fake repository honours the requested start date, so a short window
    fails here the same way it did against DynamoDB.
    """
    now = datetime(2026, 10, day, 22, 0)
    clock(now)
    use_prices(random_walk_prices(ALL_TICKERS, days=900, seed=day, end=now))

    result = run_monthly_walkforward_backtest(SPECS[strategy_id], SPECS[strategy_id].default_parameters())

    assert "error" not in result, result
    assert result["metrics"]["months_tested"] == 12
    assert result["metrics"]["as_of"] == "2026-09-30"


# --- Runner -----------------------------------------------------------------

def test_runner_returns_payload_locally_without_storing(use_prices, clock):
    use_prices(make_prices({"SPY": 0.001, "AGG": 0.0002}, days=800, end=TODAY))
    result = runner.compute_and_store_for_strategy("sixty_forty")
    assert result["ok"] is True
    assert result["persisted"] is False
    assert result["payload"]["strategy_id"] == "sixty_forty"
    assert result["payload"]["metrics"]["months_tested"] == 12


def test_runner_reports_storage_failure_when_storage_is_on(use_prices, clock, monkeypatch):
    monkeypatch.setattr(runner, "performance_enabled", lambda: True)
    monkeypatch.setattr(runner, "performance_set_metrics", lambda *_: False)
    use_prices(make_prices({"SPY": 0.001, "AGG": 0.0002}, days=800, end=TODAY))
    result = runner.compute_and_store_for_strategy("sixty_forty")
    assert result["ok"] is False
    assert "persist" in result["error"]


def test_runner_saves_payload_when_storage_is_on(use_prices, clock, monkeypatch):
    saved = {}
    monkeypatch.setattr(runner, "performance_set_metrics", lambda sid, payload: saved.update({sid: payload}) or True)
    use_prices(make_prices({"SPY": 0.001, "AGG": 0.0002}, days=800, end=TODAY))
    result = runner.compute_and_store_for_strategy("sixty_forty")
    assert result["ok"] is True and "payload" not in result
    assert saved["sixty_forty"]["strategy_name"] == "60/40 Portfolio"


def test_runner_unknown_strategy():
    assert runner.compute_and_store_for_strategy("nope")["ok"] is False


def test_monthly_refresh_runs_every_spec(monkeypatch):
    monkeypatch.setattr(runner, "compute_and_store_for_strategy", lambda sid: {"ok": sid != "vaa"})
    summary = runner.run_monthly_performance_refresh()
    assert summary["total"] == len(SPECS)
    assert summary["updated"] == len(SPECS) - 1
    assert summary["ok"] is False

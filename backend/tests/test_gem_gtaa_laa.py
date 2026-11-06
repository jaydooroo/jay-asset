"""Decision rules of the strategies written as pure compute_* functions."""
import pandas as pd
import pytest

from helpers import make_prices
from strategies.gem_strategy import compute_gem
from strategies.gtaa_strategy import compute_gtaa, normalize_tickers
from strategies.laa_strategy import compute_laa

UP, SLIGHTLY_UP, DOWN = 0.001, 0.0001, -0.001


# --- GEM -------------------------------------------------------------------

class TestGEM:
    def test_holds_us_stocks_when_they_beat_cash_and_international(self):
        prices = make_prices({"SPY": UP, "EFA": SLIGHTLY_UP, "AGG": SLIGHTLY_UP, "BIL": SLIGHTLY_UP})
        result = compute_gem(prices)
        assert result["selected_asset"] == "SPY"
        assert result["allocation_weights"] == {"SPY": 1.0}

    def test_holds_international_when_it_beats_us(self):
        prices = make_prices({"SPY": SLIGHTLY_UP * 2, "EFA": UP, "AGG": 0, "BIL": SLIGHTLY_UP})
        assert compute_gem(prices)["selected_asset"] == "EFA"

    def test_moves_to_bonds_when_us_stocks_trail_cash(self):
        # International stocks are strong here, but absolute momentum is
        # judged on SPY alone, so the answer is still bonds.
        prices = make_prices({"SPY": DOWN, "EFA": UP, "AGG": 0, "BIL": SLIGHTLY_UP})
        assert compute_gem(prices)["allocation_weights"] == {"AGG": 1.0}

    def test_falls_back_to_cash_when_bonds_are_missing(self):
        prices = make_prices({"SPY": DOWN, "EFA": UP, "BIL": SLIGHTLY_UP})
        result = compute_gem(prices)
        assert result["allocation_weights"] == {"BIL": 1.0}
        assert result["missing_tickers"] == ["AGG"]

    def test_tie_between_us_and_international_goes_to_us(self):
        prices = make_prices({"SPY": UP, "EFA": UP, "AGG": 0, "BIL": 0})
        assert compute_gem(prices)["selected_asset"] == "SPY"

    def test_us_equal_to_cash_is_not_enough_to_hold_stocks(self):
        prices = make_prices({"SPY": SLIGHTLY_UP, "EFA": UP, "AGG": 0, "BIL": SLIGHTLY_UP})
        assert compute_gem(prices)["selected_asset"] == "AGG"

    def test_shorter_lookback_needs_less_history(self):
        prices = make_prices({"SPY": UP, "EFA": 0, "AGG": 0, "BIL": 0}, days=70)
        assert "error" in compute_gem(prices, lookback_months=12)
        assert compute_gem(prices, lookback_months=3)["selected_asset"] == "SPY"

    @pytest.mark.parametrize("days", [252, 1])
    def test_errors_without_a_full_lookback(self, days):
        prices = make_prices({"SPY": UP, "EFA": UP, "AGG": UP, "BIL": UP}, days=days)
        result = compute_gem(prices)
        assert "error" in result
        assert {"SPY", "BIL"} <= set(result["missing_tickers"])

    def test_errors_without_cash(self):
        prices = make_prices({"SPY": UP, "EFA": UP, "AGG": UP})
        assert compute_gem(prices)["missing_tickers"] == ["BIL"]


# --- GTAA ------------------------------------------------------------------

RISK = ["SPY", "EFA", "IEF", "DBC", "VNQ"]


class TestGTAA:
    def test_all_trending_up_is_fully_invested_in_equal_slices(self):
        prices = make_prices({t: UP for t in RISK})
        result = compute_gtaa(prices, RISK)
        assert result["allocation_weights"] == {t: 0.2 for t in RISK}
        assert result["offensive_ratio"] == 1.0

    def test_assets_below_their_average_move_to_cash(self):
        prices = make_prices({"SPY": UP, "EFA": DOWN, "IEF": UP, "DBC": DOWN, "VNQ": DOWN})
        result = compute_gtaa(prices, RISK)
        assert result["allocation_weights"] == {"SPY": 0.2, "IEF": 0.2, "BIL": 0.6}
        assert result["selected_offensive"] == ["SPY", "IEF"]

    def test_all_trending_down_is_all_cash(self):
        prices = make_prices({t: DOWN for t in RISK})
        assert compute_gtaa(prices, RISK)["allocation_weights"] == {"BIL": pytest.approx(1.0)}

    def test_price_exactly_on_its_average_is_not_a_buy(self):
        prices = make_prices({"SPY": 0.0, "EFA": UP})
        assert compute_gtaa(prices, ["SPY", "EFA"])["allocation_weights"] == {"BIL": 0.5, "EFA": 0.5}

    def test_missing_asset_keeps_its_slice_in_cash(self):
        prices = make_prices({"SPY": UP, "EFA": UP})
        result = compute_gtaa(prices, ["SPY", "EFA", "VNQ", "DBC"])
        assert result["allocation_weights"] == {"SPY": 0.25, "EFA": 0.25, "BIL": 0.5}
        assert result["missing_tickers"] == ["VNQ", "DBC"]

    def test_custom_cash_asset(self):
        prices = make_prices({"SPY": DOWN})
        assert compute_gtaa(prices, ["SPY"], cash_asset="SHY")["allocation_weights"] == {"SHY": 1.0}

    def test_needs_sma_months_of_month_ends(self):
        prices = make_prices({"SPY": UP}, days=120)  # about 6 month-ends
        assert "error" in compute_gtaa(prices, ["SPY"], sma_months=10)
        assert compute_gtaa(prices, ["SPY"], sma_months=4)["allocation_weights"] == {"SPY": 1.0}

    def test_no_risk_assets_is_an_error(self):
        assert "error" in compute_gtaa(make_prices({"SPY": UP}), [])

    def test_average_covers_the_last_n_month_ends_including_this_month(self):
        # Month-end closes: 50, then nine months at 100, then 96 now.
        # 10-month average = (9 * 100 + 96) / 10 = 99.6, so 96 is below it.
        # Averaging the ten months before this one (= 95) would wrongly buy.
        closes = [50.0] + [100.0] * 9 + [96.0]
        days = pd.bdate_range("2025-11-03", "2026-09-15")
        months = days.to_period("M")
        first = months[0]
        prices = pd.DataFrame({"SPY": [closes[(m - first).n] for m in months]}, index=days)

        result = compute_gtaa(prices, ["SPY"], sma_months=10)
        assert result["momentum_scores"]["SPY"] == pytest.approx(96 / 99.6 - 1, abs=1e-6)
        assert result["allocation_weights"] == {"BIL": 1.0}

    def test_normalize_tickers(self):
        assert normalize_tickers(" spy, efa ,SPY,,") == ["SPY", "EFA"]
        assert normalize_tickers(["ief", "IEF"]) == ["IEF"]
        assert normalize_tickers(None) == []


# --- LAA -------------------------------------------------------------------

LAA_FIXED = {"IWD": UP, "GLD": UP, "IEF": UP, "QQQ": UP, "SHY": SLIGHTLY_UP}


class TestLAA:
    def test_holds_nasdaq_while_sp500_is_above_its_200_day_average(self):
        result = compute_laa(make_prices({**LAA_FIXED, "SPY": UP}))
        assert result["selected_asset"] == "QQQ"
        assert result["allocation_weights"] == {"IWD": 0.25, "GLD": 0.25, "IEF": 0.25, "QQQ": 0.25}

    def test_moves_timing_slice_to_short_bonds_in_a_downtrend(self):
        result = compute_laa(make_prices({**LAA_FIXED, "SPY": DOWN}))
        assert result["selected_asset"] == "SHY"
        assert result["allocation_weights"] == {"IWD": 0.25, "GLD": 0.25, "IEF": 0.25, "SHY": 0.25}

    def test_flat_market_counts_as_downtrend(self):
        assert compute_laa(make_prices({**LAA_FIXED, "SPY": 0.0}))["selected_asset"] == "SHY"

    def test_fixed_part_ignores_the_signal(self):
        up = compute_laa(make_prices({**LAA_FIXED, "SPY": UP}))["allocation_weights"]
        down = compute_laa(make_prices({**LAA_FIXED, "SPY": DOWN}))["allocation_weights"]
        for ticker in ("IWD", "GLD", "IEF"):
            assert up[ticker] == down[ticker] == 0.25

    def test_needs_200_days_of_sp500(self):
        assert "error" in compute_laa(make_prices({**LAA_FIXED, "SPY": UP}, days=199))
        assert "error" not in compute_laa(make_prices({**LAA_FIXED, "SPY": UP}, days=200))

    def test_errors_without_sp500(self):
        assert compute_laa(make_prices(LAA_FIXED))["missing_tickers"] == ["SPY"]

    def test_reports_held_tickers_without_prices(self):
        # The IWD gap that showed up in production: the plan still lists IWD,
        # but the result must flag it so the UI can warn.
        prices = make_prices({"GLD": UP, "IEF": UP, "QQQ": UP, "SHY": 0, "SPY": UP})
        assert compute_laa(prices)["missing_tickers"] == ["IWD"]

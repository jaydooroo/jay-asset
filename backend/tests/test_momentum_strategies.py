"""
PAA, VAA, CDM and DAA read prices themselves, so these tests install a fake
price repository and call `calculate_plan` the way the API does.
"""
import numpy as np
import pytest

from helpers import make_prices
from performance.specs import SPECS
from strategies import CDMStrategy, DAAStrategy, PAAStrategy, VAAStrategy

UP, SLIGHTLY_UP, DOWN = 0.001, 0.0002, -0.001


def weights_of(plan):
    assert "error" not in plan, plan
    return plan["allocation_weights"]


# --- PAA -------------------------------------------------------------------

PAA_ETFS = ["SPY", "QQQ", "IWM", "VGK", "EWJ", "EEM", "VNQ", "GLD", "DBC", "HYG", "LQD"]


def paa_prices(n_negative):
    """The first `n_negative` ETFs trend down, the rest trend up (later ones stronger)."""
    drifts = {t: (DOWN if i < n_negative else UP * (1 + i / 10)) for i, t in enumerate(PAA_ETFS)}
    return make_prices({**drifts, "IEF": SLIGHTLY_UP})


class TestPAA:
    def test_all_positive_momentum_is_fully_offensive_in_top_six(self, use_prices):
        use_prices(paa_prices(0))
        plan = PAAStrategy().calculate_plan()
        assert weights_of(plan) == pytest.approx({t: 1 / 6 for t in PAA_ETFS[-6:]})
        assert plan["selected_etfs"] == PAA_ETFS[::-1][:6]
        assert plan["defensive_ratio"] == 0

    @pytest.mark.parametrize("n_negative, bond_share", [(1, 1 / 6), (2, 2 / 6), (3, 3 / 6), (5, 5 / 6)])
    def test_each_negative_etf_moves_one_sixth_into_bonds(self, use_prices, n_negative, bond_share):
        use_prices(paa_prices(n_negative))
        weights = weights_of(PAAStrategy().calculate_plan())
        assert weights["IEF"] == pytest.approx(bond_share)
        offensive = {t: w for t, w in weights.items() if t != "IEF"}
        assert len(offensive) == 6
        assert sum(offensive.values()) == pytest.approx(1 - bond_share)

    @pytest.mark.parametrize("n_negative", [6, 8, 11])
    def test_six_or_more_negative_is_all_bonds(self, use_prices, n_negative):
        use_prices(paa_prices(n_negative))
        weights = weights_of(PAAStrategy().calculate_plan())
        assert weights["IEF"] == pytest.approx(1.0)
        assert all(w == 0 for t, w in weights.items() if t != "IEF")

    def test_top_n_parameter(self, use_prices):
        use_prices(paa_prices(0))
        weights = weights_of(PAAStrategy().calculate_plan(top_n=3))
        assert weights == pytest.approx({t: 1 / 3 for t in PAA_ETFS[-3:]})

    def test_top_n_larger_than_universe_uses_every_etf(self, use_prices):
        use_prices(make_prices({"SPY": UP, "QQQ": UP, "IEF": 0}))
        weights = weights_of(PAAStrategy().calculate_plan(etfs=["SPY", "QQQ"], top_n=6))
        assert weights == pytest.approx({"SPY": 0.5, "QQQ": 0.5})

    def test_missing_etf_is_skipped_and_reported(self, use_prices):
        use_prices(paa_prices(0).drop(columns=["EWJ"]))
        plan = PAAStrategy().calculate_plan()
        assert "EWJ" not in weights_of(plan)
        assert plan["missing_tickers"] == ["EWJ"]

    def test_too_little_history_is_an_error(self, use_prices):
        use_prices(make_prices({t: UP for t in PAA_ETFS + ["IEF"]}, days=200))
        assert "Insufficient data" in PAAStrategy().calculate_plan()["error"]

    def test_no_stored_prices_is_an_error(self, use_prices):
        use_prices(make_prices({"XYZ": UP}))
        plan = PAAStrategy().calculate_plan()
        assert "error" in plan
        assert "SPY" in plan["missing_tickers"]

    def test_accepts_comma_separated_etfs(self, use_prices):
        use_prices(paa_prices(0))
        plan = PAAStrategy().calculate_plan(etfs=" spy,qqq ", top_n="2")
        assert weights_of(plan) == pytest.approx({"SPY": 0.5, "QQQ": 0.5})

    def test_non_numeric_settings_are_an_error_not_a_crash(self, use_prices):
        use_prices(paa_prices(0))
        assert "error" in PAAStrategy().calculate_plan(top_n="abc")

    @pytest.mark.parametrize("months", [6, 9, 12, 24])
    def test_lookback_months_sets_the_moving_average_window(self, use_prices, months):
        use_prices(make_prices({t: UP for t in PAA_ETFS + ["IEF"]}, days=600))
        plan = PAAStrategy().calculate_plan(lookback_months=months)
        assert "error" not in plan, plan

    def test_lookback_months_changes_the_decision(self, use_prices):
        # SPY rose for a year, then slipped about 4% over the last two months:
        # still above its 12-month average, but below its 3-month average.
        prices = make_prices({t: UP for t in PAA_ETFS + ["IEF"]}, days=400)
        spy = prices["SPY"].to_numpy().copy()
        spy[-42:] = spy[-43] * (1 - UP) ** np.arange(1, 43)
        prices["SPY"] = spy
        use_prices(prices)

        long_view = PAAStrategy().calculate_plan(lookback_months=12)
        short_view = PAAStrategy().calculate_plan(lookback_months=3)
        assert long_view["momentum_scores"]["SPY"] > 0
        assert short_view["momentum_scores"]["SPY"] < 0
        assert short_view["num_negative_momentum"] == long_view["num_negative_momentum"] + 1

    def test_lookback_needs_that_much_history(self, use_prices):
        use_prices(make_prices({t: UP for t in PAA_ETFS + ["IEF"]}, days=300))
        assert "need at least 504 days" in PAAStrategy().calculate_plan(lookback_months=24)["error"]


# --- VAA -------------------------------------------------------------------

VAA_OFFENSIVE = ["SPY", "EFA", "EEM", "AGG"]
VAA_DEFENSIVE = ["LQD", "IEF", "SHY"]


class TestVAA:
    def test_all_offensive_positive_holds_the_strongest_one(self, use_prices):
        use_prices(make_prices({"SPY": UP, "EFA": UP * 2, "EEM": UP, "AGG": SLIGHTLY_UP,
                                "LQD": UP * 3, "IEF": 0, "SHY": 0}))
        plan = VAAStrategy().calculate_plan()
        assert weights_of(plan) == {"EFA": 1.0}
        assert plan["mode"] == "offensive"

    def test_a_single_negative_offensive_asset_goes_fully_defensive(self, use_prices):
        use_prices(make_prices({"SPY": UP * 3, "EFA": UP, "EEM": DOWN, "AGG": UP,
                                "LQD": DOWN, "IEF": SLIGHTLY_UP, "SHY": 0}))
        plan = VAAStrategy().calculate_plan()
        assert weights_of(plan) == {"IEF": 1.0}
        assert plan["mode"] == "defensive"

    def test_defensive_pick_is_the_least_bad_when_all_fall(self, use_prices):
        use_prices(make_prices({**{t: DOWN for t in VAA_OFFENSIVE},
                                "LQD": DOWN * 2, "IEF": DOWN, "SHY": DOWN / 4}))
        assert weights_of(VAAStrategy().calculate_plan()) == {"SHY": 1.0}

    def test_score_weights_recent_months_most(self, use_prices):
        # 12*R1 + 4*R3 + 2*R6 + R12: a sharp drop in the last month outweighs
        # a year of gains, which is what makes VAA fast to exit.
        prices = make_prices({t: UP for t in VAA_OFFENSIVE + VAA_DEFENSIVE})
        prices.iloc[-21:, prices.columns.get_loc("EEM")] *= 0.85
        use_prices(prices)
        plan = VAAStrategy().calculate_plan()
        assert plan["momentum_scores"]["EEM"] < 0
        assert plan["mode"] == "defensive"

    def test_accepts_comma_separated_custom_universe(self, use_prices):
        use_prices(make_prices({"QQQ": UP, "SPY": SLIGHTLY_UP, "TLT": 0}))
        plan = VAAStrategy().calculate_plan(offensive_assets=" qqq, spy ", defensive_assets="tlt")
        assert weights_of(plan) == {"QQQ": 1.0}

    def test_missing_required_asset_is_an_error(self, use_prices):
        use_prices(make_prices({t: UP for t in VAA_OFFENSIVE + ["LQD", "IEF"]}))
        plan = VAAStrategy().calculate_plan()
        assert "error" in plan
        assert "SHY" in plan["missing_tickers"]


# --- CDM -------------------------------------------------------------------

CDM_TICKERS = ["SPY", "EFA", "LQD", "HYG", "VNQ", "REM", "TLT", "GLD", "BIL"]


class TestCDM:
    def test_each_sleeve_holds_its_stronger_asset(self, use_prices):
        use_prices(make_prices({"SPY": UP, "EFA": SLIGHTLY_UP * 2, "LQD": SLIGHTLY_UP * 2, "HYG": UP,
                                "VNQ": UP * 2, "REM": UP, "TLT": UP, "GLD": UP * 2, "BIL": SLIGHTLY_UP}))
        plan = CDMStrategy().calculate_plan()
        assert weights_of(plan) == pytest.approx({"SPY": 0.25, "HYG": 0.25, "VNQ": 0.25, "GLD": 0.25})
        assert plan["selected_by_sleeve"] == {"equity": "SPY", "credit": "HYG", "reit": "VNQ", "hedge": "GLD"}

    def test_sleeve_trailing_cash_moves_to_cash(self, use_prices):
        use_prices(make_prices({"SPY": UP, "EFA": DOWN, "LQD": DOWN, "HYG": 0,
                                "VNQ": DOWN, "REM": DOWN, "TLT": UP, "GLD": 0, "BIL": SLIGHTLY_UP}))
        plan = CDMStrategy().calculate_plan()
        assert weights_of(plan) == pytest.approx({"SPY": 0.25, "BIL": 0.5, "TLT": 0.25})
        assert plan["selected_by_sleeve"]["credit"] == "BIL"

    def test_all_sleeves_trailing_cash_is_all_cash(self, use_prices):
        use_prices(make_prices({**{t: DOWN for t in CDM_TICKERS}, "BIL": SLIGHTLY_UP}))
        assert weights_of(CDMStrategy().calculate_plan()) == pytest.approx({"BIL": 1.0})

    def test_tie_inside_a_sleeve_goes_to_the_alphabetically_first(self, use_prices):
        use_prices(make_prices({**{t: UP for t in CDM_TICKERS}, "BIL": 0}))
        assert CDMStrategy().calculate_plan()["selected_by_sleeve"] == {
            "equity": "EFA", "credit": "HYG", "reit": "REM", "hedge": "GLD"}

    def test_custom_pairs_and_lookback(self, use_prices):
        use_prices(make_prices({**{t: UP for t in CDM_TICKERS}, "QQQ": UP * 3, "BIL": 0}))
        plan = CDMStrategy().calculate_plan(equity_assets="qqq,spy", lookback_months="6")
        assert plan["selected_by_sleeve"]["equity"] == "QQQ"
        assert plan["lookback_months"] == 6

    def test_sleeve_equal_to_cash_keeps_its_asset(self, use_prices):
        # Cash wins only when it is strictly better. Live plan and backtest
        # spec must agree on this edge.
        prices = make_prices({**{t: UP for t in CDM_TICKERS}, "SPY": SLIGHTLY_UP, "EFA": SLIGHTLY_UP,
                              "BIL": SLIGHTLY_UP})
        use_prices(prices)
        assert CDMStrategy().calculate_plan()["selected_by_sleeve"]["equity"] == "EFA"
        spec = SPECS["cdm"]
        assert "EFA" in spec.compute_weights(prices, spec.default_parameters())["allocation_weights"]

    def test_any_missing_ticker_is_an_error(self, use_prices):
        use_prices(make_prices({t: UP for t in CDM_TICKERS if t != "REM"}))
        assert "REM" in CDMStrategy().calculate_plan()["error"]


# --- DAA -------------------------------------------------------------------

DAA_OFFENSIVE = ["SPY", "QQQ", "IWM", "VGK", "EWJ", "EEM", "VNQ", "GLD", "DBC", "HYG", "LQD", "TLT"]


def daa_prices(vwo, bnd, defensive=None):
    drifts = {t: UP * (1 + i / 10) for i, t in enumerate(DAA_OFFENSIVE)}  # TLT strongest
    drifts.update({"LQD": SLIGHTLY_UP, "IEF": SLIGHTLY_UP * 2, "SHY": SLIGHTLY_UP / 2})
    drifts.update(defensive or {})
    drifts.update({"VWO": vwo, "BND": bnd})
    return make_prices(drifts)


TOP6 = ["TLT", "HYG", "DBC", "GLD", "VNQ", "EEM"]


class TestDAA:
    def test_both_canaries_positive_is_fully_offensive(self, use_prices):
        use_prices(daa_prices(UP, UP))
        plan = DAAStrategy().calculate_plan()
        assert weights_of(plan) == pytest.approx({t: 1 / 6 for t in TOP6}, abs=1e-6)
        assert plan["selected_offensive"] == TOP6
        assert plan["offensive_ratio"] == 1.0

    def test_one_canary_negative_is_half_offensive(self, use_prices):
        use_prices(daa_prices(UP, DOWN))
        weights = weights_of(DAAStrategy().calculate_plan())
        assert weights["IEF"] == pytest.approx(0.5)
        assert {t: w for t, w in weights.items() if t != "IEF"} == pytest.approx({t: 1 / 12 for t in TOP6}, abs=1e-6)

    def test_both_canaries_negative_is_fully_defensive(self, use_prices):
        use_prices(daa_prices(DOWN, DOWN))
        assert weights_of(DAAStrategy().calculate_plan()) == {"IEF": 1.0}

    def test_canary_at_exactly_zero_counts_as_positive(self, use_prices):
        use_prices(daa_prices(0.0, 0.0))
        assert DAAStrategy().calculate_plan()["offensive_ratio"] == 1.0

    def test_asset_in_both_lists_gets_both_slices(self, use_prices):
        # LQD is offensive and defensive by default; make it the top pick of both.
        use_prices(daa_prices(UP, DOWN, defensive={"LQD": UP * 5}))
        weights = weights_of(DAAStrategy().calculate_plan())
        assert weights["LQD"] == pytest.approx(1 / 12 + 0.5, abs=1e-6)
        assert sum(weights.values()) == pytest.approx(1.0, abs=1e-5)

    def test_top_n_parameter(self, use_prices):
        use_prices(daa_prices(UP, UP))
        assert weights_of(DAAStrategy().calculate_plan(top_n="2")) == pytest.approx({"TLT": 0.5, "HYG": 0.5})

    def test_without_canary_data_is_an_error(self, use_prices):
        use_prices(daa_prices(UP, UP).drop(columns=["VWO", "BND"]))
        assert "canary" in DAAStrategy().calculate_plan()["error"]

"""Cache keys (cache/keys.py) and turning weights into money (scale_plan, calculate_allocation)."""
import re

import pytest

from cache import cache_key, scale_plan
from strategies import STRATEGIES


class TestCacheKey:
    @pytest.mark.parametrize("strategy_id, a, b", [
        ("paa", {"etfs": "spy, qqq", "top_n": "6"}, {"etfs": ["QQQ", "SPY", "SPY"], "top_n": 6}),
        ("vaa", {"offensive_assets": "spy,efa"}, {"offensive_assets": ["EFA", "SPY"]}),
        ("cdm", {"cash_asset": " bil ", "lookback_months": "12"}, {"cash_asset": "BIL", "lookback_months": 12}),
        ("daa", {"canary_assets": "vwo,bnd", "top_n": "6"}, {"canary_assets": ["BND", "VWO"], "top_n": 6}),
        ("gem", {"lookback_months": "12"}, {"lookback_months": 12.0}),
        ("gtaa", {"risk_assets": "spy,efa", "sma_months": "10"}, {"risk_assets": ["EFA", "SPY"], "sma_months": 10}),
        ("sixty_forty", {"weights": "SPY:60,AGG:40"}, {"weights": {"AGG": 4, "SPY": 6}}),
    ])
    def test_equivalent_inputs_share_one_key(self, strategy_id, a, b):
        strategy = STRATEGIES[strategy_id]
        assert cache_key(strategy_id, a, strategy) == cache_key(strategy_id, b, strategy)

    def test_different_inputs_get_different_keys(self):
        strategy = STRATEGIES["paa"]
        assert cache_key("paa", {"top_n": 6}, strategy) != cache_key("paa", {"top_n": 5}, strategy)
        assert cache_key("paa", {}, strategy) != cache_key("vaa", {}, STRATEGIES["vaa"])

    def test_key_rotates_daily_and_tracks_code_version(self):
        key = cache_key("laa", {}, STRATEGIES["laa"])
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}\|laa@[0-9a-f]{8}\|\{\}", key)

    def test_strategies_in_different_files_have_different_versions(self):
        version = lambda sid: cache_key(sid, {}, STRATEGIES[sid]).split("|")[1].split("@")[1]  # noqa: E731
        assert version("paa") != version("vaa")
        assert version("sixty_forty") == version("permanent")  # same class, same source

    def test_unserializable_parameters_disable_caching(self):
        assert cache_key("paa", {"etfs": object()}, STRATEGIES["paa"]) is None


class TestScalePlan:
    def test_amounts_add_up_to_the_total_despite_rounding(self):
        result = scale_plan({"allocation_weights": {"A": 1 / 3, "B": 1 / 3, "C": 1 / 3}}, 1000, "X")
        assert sum(result["allocation"].values()) == pytest.approx(1000, abs=1e-9)
        assert sorted(result["allocation"].values()) == [333.33, 333.33, 333.34]

    def test_zero_weights_get_no_line(self):
        result = scale_plan({"allocation_weights": {"IEF": 1.0, "SPY": 0.0}}, 500, "PAA")
        assert result["allocation"] == {"IEF": 500.0}

    def test_keeps_plan_metadata(self):
        result = scale_plan({"allocation_weights": {"SPY": 1.0}, "selected_asset": "SPY"}, 10, "GEM")
        assert result["selected_asset"] == "SPY"
        assert result["strategy"] == "GEM"
        assert result["total_amount"] == 10.0

    def test_plan_without_weights_is_an_error(self):
        assert "error" in scale_plan({}, 100, "X")


def test_calculate_allocation_matches_scale_plan():
    strategy = STRATEGIES["all_weather"]
    direct = strategy.calculate_allocation(12345.67)
    via_cache = scale_plan(strategy.calculate_plan(), 12345.67, strategy.name)
    assert direct == via_cache
    assert sum(direct["allocation"].values()) == pytest.approx(12345.67, abs=1e-6)


def test_calculate_allocation_passes_errors_through():
    assert "error" in STRATEGIES["sixty_forty"].calculate_allocation(100, weights="bad")

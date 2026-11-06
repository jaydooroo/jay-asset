import pytest

from strategies.static_allocation import (
    STATIC_PORTFOLIOS,
    StaticAllocationStrategy,
    build_static_strategies,
    format_weights,
    parse_weights,
)


class TestParseWeights:
    def test_text_input_is_normalized_to_fractions(self):
        assert parse_weights("SPY:60,AGG:40") == {"AGG": 0.4, "SPY": 0.6}

    def test_dict_input(self):
        assert parse_weights({"SPY": 6, "AGG": 4}) == {"AGG": 0.4, "SPY": 0.6}

    def test_weights_need_not_sum_to_100(self):
        assert parse_weights("SPY:1,TLT:1,GLD:2") == {"GLD": 0.5, "SPY": 0.25, "TLT": 0.25}

    def test_cleans_case_spaces_and_percent_signs(self):
        assert parse_weights(" spy : 60% , agg:40 ") == {"AGG": 0.4, "SPY": 0.6}

    def test_repeated_tickers_are_added(self):
        assert parse_weights("SPY:30,AGG:50,SPY:20") == {"AGG": 0.5, "SPY": 0.5}

    def test_skips_bad_zero_and_negative_entries(self):
        assert parse_weights("SPY:abc,AGG:0,TLT:-5,GLD:10,junk") == {"GLD": 1.0}

    @pytest.mark.parametrize("value", ["", "SPY", "SPY:0", None, 42, []])
    def test_nothing_valid_returns_empty(self, value):
        assert parse_weights(value) == {}


def test_format_weights_round_trips():
    weights = parse_weights("SPY:30,TLT:40,IEF:15,GLD:7.5,DBC:7.5")
    assert format_weights(weights) == "DBC:7.5,GLD:7.5,IEF:15,SPY:30,TLT:40"
    assert parse_weights(format_weights(weights)) == weights


class TestStaticAllocationStrategy:
    def test_default_plan_uses_portfolio_weights(self):
        strategy = StaticAllocationStrategy("60/40", "", {"SPY": 60, "AGG": 40})
        assert strategy.calculate_plan() == {
            "allocation_weights": {"AGG": 0.4, "SPY": 0.6},
            "rebalance": "annual",
        }

    def test_user_weights_override_defaults(self):
        strategy = StaticAllocationStrategy("60/40", "", {"SPY": 60, "AGG": 40})
        plan = strategy.calculate_plan(weights="SPY:80,AGG:20")
        assert plan["allocation_weights"] == {"AGG": 0.2, "SPY": 0.8}

    def test_invalid_user_weights_are_an_error_not_the_default(self):
        strategy = StaticAllocationStrategy("60/40", "", {"SPY": 60, "AGG": 40})
        assert "error" in strategy.calculate_plan(weights="nonsense")

    def test_ui_default_parameter_matches_portfolio(self):
        strategy = StaticAllocationStrategy("60/40", "", {"SPY": 60, "AGG": 40})
        [param] = strategy.get_parameters()
        assert param["name"] == "weights"
        assert parse_weights(param["default"]) == strategy.default_weights

    def test_category_is_static(self):
        assert StaticAllocationStrategy("x", "", {"SPY": 1}).to_dict()["category"] == "static"


@pytest.mark.parametrize("strategy_id", sorted(STATIC_PORTFOLIOS))
def test_published_portfolios_match_their_descriptions(strategy_id):
    expected = {
        "sixty_forty": {"SPY": 0.6, "AGG": 0.4},
        "permanent": {"SPY": 0.25, "TLT": 0.25, "GLD": 0.25, "BIL": 0.25},
        "all_weather": {"SPY": 0.3, "TLT": 0.4, "IEF": 0.15, "GLD": 0.075, "DBC": 0.075},
        "golden_butterfly": {"SPY": 0.2, "VBR": 0.2, "TLT": 0.2, "SHY": 0.2, "GLD": 0.2},
    }[strategy_id]
    plan = build_static_strategies()[strategy_id].calculate_plan()
    assert plan["allocation_weights"] == pytest.approx(expected)

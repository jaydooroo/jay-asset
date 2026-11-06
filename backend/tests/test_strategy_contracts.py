"""
Rules every registered strategy must follow, plus the wiring that is easy to
forget when adding one (performance spec, ingest tickers, frontend text).
See backend/NEW_STRATEGY_CHECKLIST.md.
"""
import re

import pytest
from helpers import REPO_DIR, random_walk_prices
from performance.specs import SPECS
from strategies import STRATEGIES

STRATEGY_IDS = sorted(STRATEGIES)
SEEDS = range(8)


def all_tickers():
    tickers = set()
    for spec in SPECS.values():
        tickers |= set(spec.universe(spec.default_parameters()))
    return sorted(tickers)


def positive(weights):
    return {t: w for t, w in weights.items() if w > 0}


# --- Every plan is a valid portfolio ----------------------------------------

@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("strategy_id", STRATEGY_IDS)
def test_plan_is_a_fully_invested_long_only_portfolio(use_prices, strategy_id, seed):
    use_prices(random_walk_prices(all_tickers(), seed=seed))
    plan = STRATEGIES[strategy_id].calculate_plan()

    assert "error" not in plan, plan
    weights = plan["allocation_weights"]
    assert weights, "empty allocation"
    assert all(w >= 0 for w in weights.values())
    assert sum(weights.values()) == pytest.approx(1.0, abs=1e-4)


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("strategy_id", STRATEGY_IDS)
def test_plan_only_holds_tickers_from_the_backtest_universe(use_prices, strategy_id, seed):
    use_prices(random_walk_prices(all_tickers(), seed=seed))
    spec = SPECS[strategy_id]
    held = positive(STRATEGIES[strategy_id].calculate_plan()["allocation_weights"])
    assert set(held) <= set(spec.universe(spec.default_parameters()))


# --- Live plan and backtest agree --------------------------------------------

@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("strategy_id", STRATEGY_IDS)
def test_live_plan_matches_backtest_decision(use_prices, strategy_id, seed):
    """
    PAA, VAA, CDM and DAA keep separate copies of their rules for the live
    plan and for the backtest. If the copies drift, the performance numbers
    shown on the site stop describing the strategy users follow.
    """
    prices = random_walk_prices(all_tickers(), seed=seed)
    use_prices(prices)
    spec = SPECS[strategy_id]

    live = positive(STRATEGIES[strategy_id].calculate_plan()["allocation_weights"])
    backtest = spec.compute_weights(prices, spec.default_parameters())

    assert "error" not in backtest, backtest
    assert positive(backtest["allocation_weights"]) == pytest.approx(live, abs=1e-5)


@pytest.mark.parametrize("months", [3, 6, 24])
def test_paa_live_plan_matches_backtest_for_other_lookbacks(use_prices, months):
    prices = random_walk_prices(all_tickers(), days=700, seed=months)
    use_prices(prices)
    spec = SPECS["paa"]
    live = positive(STRATEGIES["paa"].calculate_plan(lookback_months=months)["allocation_weights"])
    backtest = spec.compute_weights(prices, {"lookback_months": months})
    assert positive(backtest["allocation_weights"]) == pytest.approx(live, abs=1e-5)


# --- Registry wiring --------------------------------------------------------

def test_every_strategy_has_a_performance_spec():
    assert sorted(SPECS) == STRATEGY_IDS
    for strategy_id, spec in SPECS.items():
        assert spec.strategy_id == strategy_id


@pytest.mark.parametrize("strategy_id", STRATEGY_IDS)
def test_api_description_is_complete(strategy_id):
    info = STRATEGIES[strategy_id].to_dict()
    assert info["name"] and info["description"]
    assert info["category"] in {"static", "tactical"}
    for param in info["parameters"]:
        assert {"name", "label", "type", "default"} <= set(param)
        assert param["type"] in {"text", "number"}


def form_parameters(param_defs):
    """Mirror buildGenericParameters in src/strategies/panels/GenericConfigPanel.js."""
    out = {}
    for param in param_defs:
        raw = param["default"]
        if param["type"] == "number":
            # A JS number like 6 arrives through JSON as a Python int.
            number = float(raw)
            out[param["name"]] = int(number) if number.is_integer() else number
        elif param["name"] == "etfs" or param["name"].endswith("_assets"):
            out[param["name"]] = [t.strip().upper() for t in str(raw).split(",") if t.strip()]
        else:
            out[param["name"]] = raw
    return out


@pytest.mark.parametrize("strategy_id", STRATEGY_IDS)
def test_ui_defaults_reproduce_the_default_plan(use_prices, strategy_id):
    """Submitting the form untouched must give the same plan as sending no parameters."""
    use_prices(random_walk_prices(all_tickers(), seed=1))
    strategy = STRATEGIES[strategy_id]
    defaults = form_parameters(strategy.get_parameters())
    assert strategy.calculate_plan(**defaults)["allocation_weights"] == pytest.approx(
        strategy.calculate_plan()["allocation_weights"])


def test_every_strategy_ticker_is_ingested_daily():
    """A ticker missing here has no stored prices (the IWD/VBR gap)."""
    template = _source("template.yaml")
    line = re.search(r"MARKET_INGEST_TICKERS:\s*(\S+)", template).group(1)
    ingested = set(line.split(","))
    assert set(all_tickers()) <= ingested, sorted(set(all_tickers()) - ingested)


# --- Frontend text --------------------------------------------------------

def _source(path):
    return (REPO_DIR / path).read_text(encoding="utf-8")


def _object_keys(source, start_marker, end_marker):
    block = source.split(start_marker, 1)[1].split(end_marker, 1)[0]
    return set(re.findall(r"^  (\w+): \{", block, flags=re.M))


@pytest.mark.parametrize("language_marker", ["export const strategyEducation = {", "export const strategyEducationKo = {"])
def test_every_strategy_has_education_text(language_marker):
    keys = _object_keys(_source("src/data/strategyEducation.js"), language_marker, "\n};")
    assert set(STRATEGY_IDS) <= keys, sorted(set(STRATEGY_IDS) - keys)


@pytest.mark.parametrize("language", ["en", "ko"])
def test_every_strategy_has_a_translated_name(language):
    # Names live in two places: the `strategies` block inside the language
    # object, and the `translations.<lang>.strategies = {...}` extension.
    source = _source("src/i18n/translations.js")
    language_block = source.split(f"\n  {language}: {{", 1)[1]
    inline = language_block.split("\n    strategies: {", 1)[1].split("\n    },", 1)[0]
    keys = set(re.findall(r"^      (\w+): \{", inline, flags=re.M))
    keys |= _object_keys(source, f"translations.{language}.strategies = {{", "\n};")
    assert set(STRATEGY_IDS) <= keys, sorted(set(STRATEGY_IDS) - keys)


def test_every_ticker_has_display_metadata():
    keys = _object_keys(_source("src/data/tickerMetadata.js"), "const METADATA = {", "\n};")
    assert set(all_tickers()) <= keys, sorted(set(all_tickers()) - keys)

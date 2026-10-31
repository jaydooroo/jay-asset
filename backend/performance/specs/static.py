from __future__ import annotations

from strategies.static_allocation import STATIC_PORTFOLIOS, parse_weights

from .base import StrategyPerformanceSpec


class StaticAllocationPerformanceSpec(StrategyPerformanceSpec):
    """
    Fixed-weight portfolio backtest.

    The shared engine rebalances monthly, so results assume monthly
    rebalancing back to target weights (annual rebalancing in practice
    gives similar but not identical results).
    """

    def __init__(self, strategy_id: str):
        portfolio = STATIC_PORTFOLIOS[strategy_id]
        super().__init__(
            strategy_id=strategy_id,
            strategy_name=portfolio["name"],
            strategy_version="1",
            rebalance_frequency="monthly",
            min_lookback_days=21,
        )
        self.default_weights = parse_weights(portfolio["weights"])

    def default_parameters(self) -> dict:
        return {"weights": dict(self.default_weights)}

    def normalize_parameters(self, parameters: dict) -> dict:
        incoming = dict(parameters or {})
        weights = parse_weights(incoming.get("weights")) if "weights" in incoming else {}
        return {"weights": weights or dict(self.default_weights)}

    def universe(self, parameters: dict) -> list[str]:
        return sorted(self.normalize_parameters(parameters)["weights"].keys())

    def compute_weights(self, history, parameters: dict) -> dict:
        return {"allocation_weights": dict(self.normalize_parameters(parameters)["weights"])}


def build_static_specs() -> dict:
    return {strategy_id: StaticAllocationPerformanceSpec(strategy_id) for strategy_id in STATIC_PORTFOLIOS}

from __future__ import annotations

from strategies import gem_strategy, gtaa_strategy, laa_strategy

from .base import StrategyPerformanceSpec

# These specs reuse the pure compute_* functions from the runtime strategies,
# so the backtest and the live plan always follow the same rules.


class GEMPerformanceSpec(StrategyPerformanceSpec):
    def __init__(self):
        super().__init__(
            strategy_id="gem",
            strategy_name="GEM (Dual Momentum)",
            strategy_version="1",
            rebalance_frequency="monthly",
            min_lookback_days=253,
        )

    def default_parameters(self) -> dict:
        return {"lookback_months": gem_strategy.DEFAULT_LOOKBACK_MONTHS}

    def normalize_parameters(self, parameters: dict) -> dict:
        out = self.default_parameters()
        try:
            out["lookback_months"] = max(1, min(12, int(float((parameters or {})["lookback_months"]))))
        except Exception:
            pass
        return out

    def universe(self, parameters: dict) -> list[str]:
        return sorted(gem_strategy.UNIVERSE)

    def compute_weights(self, history, parameters: dict) -> dict:
        params = self.normalize_parameters(parameters)
        return gem_strategy.compute_gem(history, params["lookback_months"])


class GTAAPerformanceSpec(StrategyPerformanceSpec):
    def __init__(self):
        super().__init__(
            strategy_id="gtaa",
            strategy_name="GTAA (Faber Trend Following)",
            strategy_version="1",
            rebalance_frequency="monthly",
            min_lookback_days=252,
        )

    def default_parameters(self) -> dict:
        return {
            "risk_assets": list(gtaa_strategy.DEFAULT_RISK_ASSETS),
            "sma_months": gtaa_strategy.DEFAULT_SMA_MONTHS,
        }

    def normalize_parameters(self, parameters: dict) -> dict:
        out = self.default_parameters()
        incoming = dict(parameters or {})
        assets = gtaa_strategy.normalize_tickers(incoming.get("risk_assets"))
        if assets:
            out["risk_assets"] = assets
        try:
            out["sma_months"] = max(2, min(12, int(float(incoming["sma_months"]))))
        except Exception:
            pass
        return out

    def universe(self, parameters: dict) -> list[str]:
        params = self.normalize_parameters(parameters)
        return sorted(set(params["risk_assets"] + [gtaa_strategy.DEFAULT_CASH_ASSET]))

    def compute_weights(self, history, parameters: dict) -> dict:
        params = self.normalize_parameters(parameters)
        return gtaa_strategy.compute_gtaa(
            history, params["risk_assets"], gtaa_strategy.DEFAULT_CASH_ASSET, params["sma_months"]
        )


class LAAPerformanceSpec(StrategyPerformanceSpec):
    def __init__(self):
        super().__init__(
            strategy_id="laa",
            strategy_name="LAA (Lethargic Asset Allocation)",
            strategy_version="1",
            rebalance_frequency="monthly",
            min_lookback_days=laa_strategy.SMA_DAYS,
        )

    def default_parameters(self) -> dict:
        return {}

    def universe(self, parameters: dict) -> list[str]:
        return sorted(laa_strategy.UNIVERSE)

    def compute_weights(self, history, parameters: dict) -> dict:
        return laa_strategy.compute_laa(history)

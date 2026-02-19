from __future__ import annotations

from .base import StrategyPerformanceSpec


def _normalize_tickers(value):
    if isinstance(value, str):
        parts = [part.strip().upper() for part in value.split(",")]
    elif isinstance(value, list):
        parts = [str(part).strip().upper() for part in value]
    else:
        return []
    return sorted(dict.fromkeys([part for part in parts if part]))


class PAAPerformanceSpec(StrategyPerformanceSpec):
    def __init__(self):
        super().__init__(
            strategy_id="paa",
            strategy_name="PAA (Protective Asset Allocation)",
            strategy_version="1",
            rebalance_frequency="monthly",
            min_lookback_days=252,
        )
        self.default_etfs = ["SPY", "QQQ", "IWM", "VGK", "EWJ", "EEM", "VNQ", "GLD", "DBC", "HYG", "LQD"]
        self.fallback_asset = "IEF"

    def default_parameters(self) -> dict:
        return {
            "etfs": list(self.default_etfs),
            "top_n": 6,
            "lookback_months": 12,
        }

    def normalize_parameters(self, parameters: dict) -> dict:
        out = dict(self.default_parameters())
        incoming = dict(parameters or {})

        if "etfs" in incoming:
            normalized = _normalize_tickers(incoming.get("etfs"))
            if normalized:
                out["etfs"] = normalized

        for key in ("top_n", "lookback_months"):
            if key in incoming:
                try:
                    out[key] = int(float(incoming[key]))
                except Exception:
                    pass

        out["top_n"] = max(1, int(out["top_n"]))
        out["lookback_months"] = max(1, int(out["lookback_months"]))
        return out

    def universe(self, parameters: dict) -> list[str]:
        params = self.normalize_parameters(parameters)
        etfs = params.get("etfs") or []
        if self.fallback_asset not in etfs:
            etfs = list(etfs) + [self.fallback_asset]
        return sorted(dict.fromkeys(etfs))

    @staticmethod
    def _calculate_ief_ratio(num_negative_momentum: int) -> float:
        lookup = {
            0: 0.0,
            1: 1 / 6,
            2: 2 / 6,
            3: 3 / 6,
            4: 4 / 6,
            5: 5 / 6,
            6: 1.0,
        }
        return float(lookup.get(num_negative_momentum, 1.0))

    def compute_weights(self, history, parameters: dict) -> dict:
        params = self.normalize_parameters(parameters)
        etfs = params.get("etfs") or []
        top_n = int(params.get("top_n", 6))

        if history is None or history.empty:
            return {"error": "No historical data"}

        # Use a 12M moving average (252 trading days), same as runtime strategy logic.
        if len(history) < 252:
            return {"error": f"Insufficient data: need at least 252 days, got {len(history)}"}

        rolling_avg = history.rolling(window=252).mean().iloc[-1]
        current_price = history.iloc[-1]
        momentum = (current_price / rolling_avg) - 1.0
        momentum = momentum.dropna()
        if momentum.empty:
            return {"error": "Unable to calculate momentum"}

        available_etfs = [etf for etf in etfs if etf in momentum.index]
        if not available_etfs:
            return {"error": "No price data available for requested ETFs"}

        top_n = min(max(1, top_n), len(available_etfs))
        selected = momentum[available_etfs].sort_values(ascending=False).head(top_n)

        num_negative = int((momentum[available_etfs] < 0).sum())
        ief_ratio = self._calculate_ief_ratio(num_negative)
        offensive_weight_each = (1.0 - ief_ratio) / float(top_n) if top_n else 0.0

        weights = {}
        for etf in selected.index:
            if float(momentum[etf]) >= 0:
                weights[etf] = float(offensive_weight_each)

        if ief_ratio > 0:
            weights[self.fallback_asset] = float(ief_ratio)

        if not weights:
            return {"error": "No valid positive allocation weights"}

        total = sum(float(value) for value in weights.values())
        normalized = {ticker: float(value) / total for ticker, value in weights.items() if float(value) > 0}
        if not normalized:
            return {"error": "No valid positive allocation weights"}

        return {"allocation_weights": normalized}


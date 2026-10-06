from __future__ import annotations

from .base import StrategyPerformanceSpec


def _normalize_tickers(value) -> list[str]:
    if isinstance(value, str):
        parts = [p.strip().upper() for p in value.split(",")]
    elif isinstance(value, list):
        parts = [str(p).strip().upper() for p in value]
    else:
        return []
    return [p for p in parts if p]


class DAAPerformanceSpec(StrategyPerformanceSpec):
    def __init__(self):
        super().__init__(
            strategy_id="daa",
            strategy_name="DAA (Defensive Asset Allocation)",
            strategy_version="1",
            rebalance_frequency="monthly",
            min_lookback_days=252,
        )
        self.default_offensive = [
            "SPY", "QQQ", "IWM", "VGK", "EWJ", "EEM",
            "VNQ", "GLD", "DBC", "HYG", "LQD", "TLT",
        ]
        self.default_defensive = ["LQD", "IEF", "SHY"]
        self.default_canary = ["VWO", "BND"]

    def default_parameters(self) -> dict:
        return {
            "offensive_assets": list(self.default_offensive),
            "defensive_assets": list(self.default_defensive),
            "canary_assets": list(self.default_canary),
            "top_n": 6,
        }

    def normalize_parameters(self, parameters: dict) -> dict:
        out = dict(self.default_parameters())
        incoming = dict(parameters or {})

        for key, fallback in (
            ("offensive_assets", self.default_offensive),
            ("defensive_assets", self.default_defensive),
            ("canary_assets", self.default_canary),
        ):
            if key in incoming:
                normalized = _normalize_tickers(incoming[key])
                if normalized:
                    out[key] = normalized

        if "top_n" in incoming:
            try:
                out["top_n"] = max(1, int(float(incoming["top_n"])))
            except Exception:
                pass

        return out

    def universe(self, parameters: dict) -> list[str]:
        params = self.normalize_parameters(parameters)
        tickers = (
            list(params.get("offensive_assets", []))
            + list(params.get("defensive_assets", []))
            + list(params.get("canary_assets", []))
        )
        return sorted(dict.fromkeys([t for t in tickers if t]))

    @staticmethod
    def _series_return(close, trading_days: int):
        close = close.dropna()
        if len(close) <= trading_days:
            return None
        return float(close.iloc[-1] / close.iloc[-(trading_days + 1)] - 1.0)

    def _momentum_score(self, close):
        lookbacks = {"R1": 21, "R3": 63, "R6": 126, "R12": 252}
        r1  = self._series_return(close, lookbacks["R1"])
        r3  = self._series_return(close, lookbacks["R3"])
        r6  = self._series_return(close, lookbacks["R6"])
        r12 = self._series_return(close, lookbacks["R12"])
        if any(v is None for v in [r1, r3, r6, r12]):
            return None
        return 12 * r1 + 4 * r3 + 2 * r6 + 1 * r12

    def compute_weights(self, history, parameters: dict) -> dict:
        params = self.normalize_parameters(parameters)
        offensive = params["offensive_assets"]
        defensive = params["defensive_assets"]
        canary    = params["canary_assets"]
        top_n     = int(params["top_n"])

        if history is None or history.empty:
            return {"error": "No historical data"}

        # Score every ticker
        scores: dict[str, float] = {}
        for t in self.universe(params):
            if t not in history.columns:
                continue
            s = self._momentum_score(history[t])
            if s is not None:
                scores[t] = float(s)

        # Canary signal → offensive ratio
        scored_canary = [t for t in canary if t in scores]
        if not scored_canary:
            return {"error": "No canary asset data available"}
        positive_count = sum(1 for t in scored_canary if scores[t] >= 0)
        offensive_ratio = positive_count / len(scored_canary)
        defensive_ratio = 1.0 - offensive_ratio

        weights: dict[str, float] = {}

        scored_offensive = [t for t in offensive if t in scores]
        if offensive_ratio > 0 and scored_offensive:
            effective_n = min(top_n, len(scored_offensive))
            selected = sorted(scored_offensive, key=lambda t: scores[t], reverse=True)[:effective_n]
            each = offensive_ratio / effective_n
            for t in selected:
                weights[t] = weights.get(t, 0.0) + each

        scored_defensive = [t for t in defensive if t in scores]
        if defensive_ratio > 0 and scored_defensive:
            best_def = max(scored_defensive, key=lambda t: scores[t])
            weights[best_def] = weights.get(best_def, 0.0) + defensive_ratio

        if not weights:
            return {"error": "No valid positive allocation weights"}

        total = sum(weights.values())
        normalized = {t: v / total for t, v in weights.items() if v > 0}
        if not normalized:
            return {"error": "No valid positive allocation weights"}

        return {"allocation_weights": normalized}

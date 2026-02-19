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


class VAAPerformanceSpec(StrategyPerformanceSpec):
    def __init__(self):
        super().__init__(
            strategy_id="vaa",
            strategy_name="VAA Aggressive (Vigilant Asset Allocation)",
            strategy_version="1",
            rebalance_frequency="monthly",
            min_lookback_days=252,
        )
        self.default_offensive = ["SPY", "EFA", "EEM", "AGG"]
        self.default_defensive = ["LQD", "IEF", "SHY"]
        self.lookbacks = {
            "R1": 21,
            "R3": 63,
            "R6": 126,
            "R12": 252,
        }

    def default_parameters(self) -> dict:
        return {
            "offensive_assets": list(self.default_offensive),
            "defensive_assets": list(self.default_defensive),
        }

    def normalize_parameters(self, parameters: dict) -> dict:
        out = dict(self.default_parameters())
        incoming = dict(parameters or {})

        for key in ("offensive_assets", "defensive_assets"):
            if key in incoming:
                normalized = _normalize_tickers(incoming.get(key))
                if normalized:
                    out[key] = normalized
        return out

    def universe(self, parameters: dict) -> list[str]:
        params = self.normalize_parameters(parameters)
        out = list(params.get("offensive_assets", [])) + list(params.get("defensive_assets", []))
        return sorted(dict.fromkeys(out))

    @staticmethod
    def _series_return(close, trading_days: int):
        close = close.dropna()
        if len(close) <= trading_days:
            return None
        return float(close.iloc[-1] / close.iloc[-(trading_days + 1)] - 1.0)

    def compute_weights(self, history, parameters: dict) -> dict:
        params = self.normalize_parameters(parameters)
        offensive = params.get("offensive_assets") or []
        defensive = params.get("defensive_assets") or []
        required = list(dict.fromkeys(offensive + defensive))

        if history is None or history.empty:
            return {"error": "No historical data"}

        scores = {}
        for ticker in required:
            if ticker not in history.columns:
                continue
            series = history[ticker]
            r1 = self._series_return(series, self.lookbacks["R1"])
            r3 = self._series_return(series, self.lookbacks["R3"])
            r6 = self._series_return(series, self.lookbacks["R6"])
            r12 = self._series_return(series, self.lookbacks["R12"])
            if any(value is None for value in (r1, r3, r6, r12)):
                continue
            score = 12 * r1 + 4 * r3 + 2 * r6 + r12
            scores[ticker] = float(score)

        if not set(required).issubset(scores.keys()):
            return {"error": "Insufficient data to score all required assets"}

        risk_on = all(scores[ticker] >= 0 for ticker in offensive)
        if risk_on:
            chosen = max(offensive, key=lambda ticker: scores[ticker])
        else:
            chosen = max(defensive, key=lambda ticker: scores[ticker])

        return {"allocation_weights": {chosen: 1.0}}


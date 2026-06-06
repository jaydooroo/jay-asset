from __future__ import annotations

from .base import StrategyPerformanceSpec


def _normalize_tickers(value):
    if isinstance(value, str):
        parts = [part.strip().upper() for part in value.split(",")]
    elif isinstance(value, list):
        parts = [str(part).strip().upper() for part in value]
    else:
        return []
    return [part for part in parts if part]


class CDMPerformanceSpec(StrategyPerformanceSpec):
    def __init__(self):
        super().__init__(
            strategy_id="cdm",
            strategy_name="CDM (Composite Dual Momentum)",
            strategy_version="1",
            rebalance_frequency="monthly",
            min_lookback_days=252,
        )
        self.default_equity = ["SPY", "EFA"]
        self.default_credit = ["LQD", "HYG"]
        self.default_reit = ["VNQ", "REM"]
        self.default_hedge = ["TLT", "GLD"]
        self.default_cash = "BIL"

    def default_parameters(self) -> dict:
        return {
            "equity_assets": list(self.default_equity),
            "credit_assets": list(self.default_credit),
            "reit_assets": list(self.default_reit),
            "hedge_assets": list(self.default_hedge),
            "cash_asset": self.default_cash,
            "lookback_months": 12,
        }

    def normalize_parameters(self, parameters: dict) -> dict:
        out = dict(self.default_parameters())
        incoming = dict(parameters or {})

        for key, fallback in (
            ("equity_assets", self.default_equity),
            ("credit_assets", self.default_credit),
            ("reit_assets", self.default_reit),
            ("hedge_assets", self.default_hedge),
        ):
            if key in incoming:
                normalized = _normalize_tickers(incoming.get(key))
                out[key] = normalized[:2] if len(normalized) >= 2 else list(fallback)

        if "cash_asset" in incoming:
            cash = str(incoming.get("cash_asset") or "").strip().upper()
            if cash:
                out["cash_asset"] = cash

        if "lookback_months" in incoming:
            try:
                out["lookback_months"] = int(float(incoming["lookback_months"]))
            except Exception:
                pass
        out["lookback_months"] = max(1, int(out["lookback_months"]))
        return out

    def universe(self, parameters: dict) -> list[str]:
        params = self.normalize_parameters(parameters)
        tickers = (
            list(params.get("equity_assets", []))
            + list(params.get("credit_assets", []))
            + list(params.get("reit_assets", []))
            + list(params.get("hedge_assets", []))
            + [params.get("cash_asset", self.default_cash)]
        )
        return sorted(dict.fromkeys([ticker for ticker in tickers if ticker]))

    @staticmethod
    def _series_return(close, trading_days: int):
        close = close.dropna()
        if len(close) <= trading_days:
            return None
        return float(close.iloc[-1] / close.iloc[-(trading_days + 1)] - 1.0)

    def compute_weights(self, history, parameters: dict) -> dict:
        params = self.normalize_parameters(parameters)
        lookback_days = max(21, int(params.get("lookback_months", 12)) * 21)
        cash_asset = params.get("cash_asset", self.default_cash)

        if history is None or history.empty:
            return {"error": "No historical data"}

        required = self.universe(params)
        returns = {}
        for ticker in required:
            if ticker not in history.columns:
                continue
            ret = self._series_return(history[ticker], lookback_days)
            if ret is None:
                continue
            returns[ticker] = float(ret)

        if cash_asset not in returns:
            return {"error": f"Insufficient data to score cash asset {cash_asset}"}

        sleeves = (
            ("equity", params.get("equity_assets", [])),
            ("credit", params.get("credit_assets", [])),
            ("reit", params.get("reit_assets", [])),
            ("hedge", params.get("hedge_assets", [])),
        )

        cash_return = returns[cash_asset]
        weights = {}
        for sleeve_name, sleeve_assets in sleeves:
            if len(sleeve_assets) < 2:
                return {"error": f"{sleeve_name} sleeve must contain two assets"}
            first, second = sleeve_assets[0], sleeve_assets[1]
            if first not in returns or second not in returns:
                return {"error": f"Insufficient data to score sleeve assets for {sleeve_name}"}

            first_return = returns[first]
            second_return = returns[second]
            candidates = [(first, first_return), (second, second_return)]
            candidates.sort(key=lambda item: (-float(item[1]), str(item[0])))
            winner, winner_return = candidates[0]
            chosen = cash_asset if winner_return < cash_return else winner
            weights[chosen] = float(weights.get(chosen, 0.0) + 0.25)

        total = sum(float(value) for value in weights.values())
        if total <= 0:
            return {"error": "No valid positive allocation weights"}
        normalized = {ticker: float(value) / total for ticker, value in weights.items() if float(value) > 0}
        if not normalized:
            return {"error": "No valid positive allocation weights"}

        return {"allocation_weights": normalized}

from datetime import datetime, timedelta
from typing import Dict, List, Union

import pandas as pd

from .base_strategy import BaseStrategy
from market import get_price_repository


class CDMStrategy(BaseStrategy):
    """is 

    Portfolio is split into 4 sleeves (25% each):
      - Equity: SPY vs EFA
      - Credit: LQD vs HYG
      - Real estate: VNQ vs REM
      - Crisis hedge: TLT vs GLD

    For each sleeve, choose the better 12-month return asset.
    If both sleeve assets are below the 12-month return of cash proxy (BIL),
    allocate that sleeve to BIL.
    """

    def __init__(self):
        super().__init__(
            name="CDM (Composite Dual Momentum)",
            description=(
                "Splits capital into four sleeves and picks the stronger ETF in each sleeve by 12-month return. "
                "If both sleeve assets trail cash (BIL), that sleeve moves to BIL."
            ),
        )
        self.default_equity_assets = ["SPY", "EFA"]
        self.default_credit_assets = ["LQD", "HYG"]
        self.default_reit_assets = ["VNQ", "REM"]
        self.default_hedge_assets = ["TLT", "GLD"]
        self.default_cash_asset = "BIL"
        self.default_lookback_months = 12

    @staticmethod
    def _normalize_ticker_list(value: Union[str, List[str]], fallback: List[str]) -> List[str]:
        if isinstance(value, str):
            parts = value.split(",")
        elif isinstance(value, list):
            parts = value
        else:
            parts = fallback
        normalized = [str(item).strip().upper() for item in parts if str(item).strip()]
        if len(normalized) >= 2:
            return normalized[:2]
        return list(fallback)

    @staticmethod
    def _series_return(close: pd.Series, trading_days: int) -> float | None:
        close = close.dropna()
        if len(close) <= trading_days:
            return None
        return float(close.iloc[-1] / close.iloc[-(trading_days + 1)] - 1.0)

    def calculate_plan(self, **kwargs) -> Dict:
        equity_assets = self._normalize_ticker_list(
            kwargs.get("equity_assets", self.default_equity_assets), self.default_equity_assets
        )
        credit_assets = self._normalize_ticker_list(
            kwargs.get("credit_assets", self.default_credit_assets), self.default_credit_assets
        )
        reit_assets = self._normalize_ticker_list(kwargs.get("reit_assets", self.default_reit_assets), self.default_reit_assets)
        hedge_assets = self._normalize_ticker_list(
            kwargs.get("hedge_assets", self.default_hedge_assets), self.default_hedge_assets
        )

        lookback_months_raw = kwargs.get("lookback_months", self.default_lookback_months)
        try:
            lookback_months = max(1, int(float(lookback_months_raw)))
        except Exception:
            lookback_months = self.default_lookback_months

        cash_asset = str(kwargs.get("cash_asset", self.default_cash_asset)).strip().upper() or self.default_cash_asset
        lookback_days = max(21, lookback_months * 21)

        sleeves = {
            "equity": equity_assets,
            "credit": credit_assets,
            "reit": reit_assets,
            "hedge": hedge_assets,
        }

        tickers: List[str] = list(dict.fromkeys([*equity_assets, *credit_assets, *reit_assets, *hedge_assets, cash_asset]))
        end_date = datetime.today()
        start_date = end_date - timedelta(days=lookback_days + 120)

        try:
            price_repository = get_price_repository()
            price_data, failed = price_repository.get_close_prices(tickers, start_date, end_date)
            price_data = price_data.dropna(axis=1, how="all")
        except Exception as exc:
            return {"error": f"Failed to download data: {exc}"}
        
        if failed != None and len(failed) > 0:
            return {"error": f"Failed to download price data for tickers: {', '.join(failed)}"}


        if price_data.empty:
            return {"error": "No price data available", "missing_tickers": failed}

        returns_12m: Dict[str, float] = {}
        missing_for_calc: List[str] = []
        for ticker in tickers:
            if ticker not in price_data.columns:    
                missing_for_calc.append(ticker)
                continue
            ret = self._series_return(price_data[ticker], lookback_days)
            if ret is None:
                missing_for_calc.append(ticker)
                continue
            returns_12m[ticker] = ret

        if cash_asset not in returns_12m:
            return {
                "error": f"Insufficient data to score cash asset {cash_asset}",
                "missing_tickers": sorted(set(failed + missing_for_calc)),
            }
        cash_return = returns_12m[cash_asset]

        weights: Dict[str, float] = {}
        selected_by_sleeve: Dict[str, str] = {}

        for sleeve_name, sleeve_assets in sleeves.items():
            if len(sleeve_assets) < 2:
                return {"error": f"{sleeve_name} sleeve must contain exactly two assets"}
            first, second = sleeve_assets[0], sleeve_assets[1]
            if first not in returns_12m or second not in returns_12m:
                return {
                    "error": f"Insufficient data to score sleeve assets for {sleeve_name}",
                    "missing_tickers": sorted(set(failed + missing_for_calc)),
                }

            first_return = returns_12m[first]
            second_return = returns_12m[second]
            candidates = [(first, first_return), (second, second_return)]
            candidates.sort(key=lambda item: (-float(item[1]), str(item[0])))
            winner, winner_return = candidates[0]

            if winner_return < cash_return:
                chosen = cash_asset
            else:
                chosen = winner

            selected_by_sleeve[sleeve_name] = chosen
            weights[chosen] = float(weights.get(chosen, 0.0) + 0.25)

        total = sum(float(v) for v in weights.values())
        if total <= 0:
            return {"error": "No valid positive allocation weights"}
        normalized = {ticker: float(value) / total for ticker, value in weights.items() if float(value) > 0}

        return {
            "date": end_date.strftime("%Y-%m-%d"),
            "allocation_weights": normalized,
            "selected_by_sleeve": selected_by_sleeve,
            "momentum_scores": {ticker: round(float(ret), 6) for ticker, ret in returns_12m.items()},
            "returns_12m": {ticker: round(float(ret), 6) for ticker, ret in returns_12m.items()},
            "cash_asset": cash_asset,
            "cash_return_12m": round(float(cash_return), 6),
            "lookback_months": int(lookback_months),
            "missing_tickers": sorted(set(failed + missing_for_calc)),
        }

    def get_parameters(self):
        return [
            {
                "name": "equity_assets",
                "label": "Equity Pair",
                "type": "text",
                "default": ",".join(self.default_equity_assets),
                "description": "Two tickers for equity sleeve (e.g., SPY,EFA)",
            },
            {
                "name": "credit_assets",
                "label": "Credit Pair",
                "type": "text",
                "default": ",".join(self.default_credit_assets),
                "description": "Two tickers for credit sleeve (e.g., LQD,HYG)",
            },
            {
                "name": "reit_assets",
                "label": "REIT Pair",
                "type": "text",
                "default": ",".join(self.default_reit_assets),
                "description": "Two tickers for real-estate sleeve (e.g., VNQ,REM)",
            },
            {
                "name": "hedge_assets",
                "label": "Hedge Pair",
                "type": "text",
                "default": ",".join(self.default_hedge_assets),
                "description": "Two tickers for hedge sleeve (e.g., TLT,GLD)",
            },
            {
                "name": "cash_asset",
                "label": "Cash Proxy",
                "type": "text",
                "default": self.default_cash_asset,
                "description": "Fallback cash-like ETF ticker (e.g., BIL)",
            },
            {
                "name": "lookback_months",
                "label": "Lookback (Months)",
                "type": "number",
                "default": self.default_lookback_months,
                "min": 3,
                "max": 24,
                "description": "Lookback horizon for return comparison",
            },
        ]

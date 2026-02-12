import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Union

from .base_strategy import BaseStrategy
from market_data import download_close_prices


class VAAStrategy(BaseStrategy):
    """
    VAA Aggressive (Vigilant Asset Allocation - Aggressive)

    Momentum score:
    score = 12*R1 + 4*R3 + 2*R6 + 1*R12
    Decision:
    - If all offensive assets have score >= 0 => 100% into best offensive
    - Else => 100% into best defensive
    """

    def __init__(self):
        super().__init__(
            name="VAA Aggressive (Vigilant Asset Allocation)",
            description=(
                "Monthly momentum scoring using 1/3/6/12-month returns. "
                "If all offensive assets have non-negative momentum, invest 100% in the best offensive asset; "
                "otherwise invest 100% in the best defensive asset."
            ),
        )
        self.offensive_assets = ['SPY', 'EFA', 'EEM', 'AGG']
        self.defensive_assets =  ["LQD", "IEF", "SHY"]

        self.lookbacks = {
            "R1": 21,
            "R3": 63,
            "R6": 126,
            "R12": 252,
        }

    def get_parameters(self) -> List[Dict]:
        return [{
            "name": "offensive_assets",
            "label": "Offensive Assets (tickers)",
            "type": "text",
            "default": ",".join(self.offensive_assets),
            "description": "Comma-separated tickers (e.g., SPY,EFA,EEM,AGG)",
        },
        {
            "name": "defensive_assets",
            "label": "Defensive Assets (tickers)",
            "type": "text",
            "default": ",".join(self.defensive_assets),
            "description": "Comma-separated tickers (e.g., LQD,IEF,SHY)",
        }
        ]

    def _normalize_ticker_list(self, value: Union[str, List[str]]) -> List[str]:
        """
        Accept either:
          - "SPY,EFA,EEM,AGG" (string from UI text input), or
          - ["SPY", "EFA", "EEM", "AGG"] (already parsed list)
        and return a clean list of uppercase tickers.
        """
        if isinstance(value, str):
            parts = value.split(',')
        else:
            parts = value

        return [
            str(item).strip().upper()
            for item in parts
            if str(item).strip()
        ]

    def calculate_plan(self, **kwargs) -> Dict:
        offensive_raw = kwargs.get("offensive_assets", self.offensive_assets)
        defensive_raw = kwargs.get("defensive_assets", self.defensive_assets)

        offensive = self._normalize_ticker_list(offensive_raw)
        defensive = self._normalize_ticker_list(defensive_raw)

        tickers = list(dict.fromkeys(offensive + defensive))  # Remove duplicates while preserving order

        end_date = datetime.today()
        start_date = end_date - timedelta(days=420)  

        price_data, failed = download_close_prices(tickers, start_date, end_date)
        price_data = price_data.dropna(axis=1, how="all")

        if price_data.empty:
            return {"error": "No price data available", "missing_tickers": failed}
            
        
        def series_return(close: pd.Series, trading_days: int) -> float | None:
            close = close.dropna()
            # We need at least (trading_days + 1) points because we look back using -(trading_days + 1).
            if len(close) <= trading_days:
                return None
            
            # total return over N trading days
            return float(close.iloc[-1] / close.iloc[-(trading_days + 1)] - 1.0)
        
        scores: Dict[str, float] = {}
        missing_for_calc: List[str] = []

        for t in tickers:
            if t not in price_data.columns: 
                missing_for_calc.append(t)
                continue
            
            s = price_data[t]

            r1 = series_return(s, self.lookbacks["R1"] )
            r3 = series_return(s, self.lookbacks["R3"] )
            r6 = series_return(s, self.lookbacks["R6"] )
            r12 = series_return(s, self.lookbacks["R12"] )

            if any(v is None for v in [r1, r3, r6, r12]):
                missing_for_calc.append(t)
                continue

            score = 12*r1 + 4*r3 + 2*r6 + 1*r12
            scores[t] = round(float(score), 6)

        required = set(offensive + defensive)
        if not required.issubset(scores.keys()):
            return {
                "error": "Insufficient data to score all required assets",
                "missing_tickers": sorted(set(failed + missing_for_calc)),
                "available_scores": scores,
            }
        
        risk_on = all(scores[t] >= 0 for t in offensive)

        if risk_on: 
            chosen = max(offensive, key=lambda t: scores[t]) 
            mode = "offensive"
        else:
            chosen = max(defensive, key=lambda t: scores[t]) 
            mode = "defensive"
        
        return {
            "date": end_date.strftime("%Y-%m-%d"),
            "allocation_weights": {chosen: 1.0},
            "mode": mode,
            "selected_asset": chosen,
            "momentum_scores": scores,
            "missing_tickers": sorted(set(failed + missing_for_calc)),
        }

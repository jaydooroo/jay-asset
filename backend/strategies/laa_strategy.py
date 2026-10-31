from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd

from .base_strategy import BaseStrategy
from market import get_price_repository

FIXED_ASSETS = ["IWD", "GLD", "IEF"]
OFFENSIVE_ASSET = "QQQ"
DEFENSIVE_ASSET = "SHY"
SIGNAL_ASSET = "SPY"
SMA_DAYS = 200
UNIVERSE = FIXED_ASSETS + [OFFENSIVE_ASSET, DEFENSIVE_ASSET, SIGNAL_ASSET]


def compute_laa(history: pd.DataFrame) -> Dict:
    """
    Pure LAA decision as of the last row of `history` (daily close prices).

    75% is fixed (IWD, GLD, IEF at 25% each). The last 25% holds QQQ while
    SPY is above its 200-day moving average, and SHY otherwise.

    Simplified: Keller's original also requires US unemployment to be above
    its 12-month average before switching to SHY. That data is not stored
    here, so this version switches on the price signal alone and is
    therefore somewhat more defensive than the original.
    """
    if history is None or SIGNAL_ASSET not in history.columns:
        return {'error': f'No price data for {SIGNAL_ASSET}', 'missing_tickers': [SIGNAL_ASSET]}

    spy = history[SIGNAL_ASSET].dropna()
    if len(spy) < SMA_DAYS:
        return {'error': f'Need {SMA_DAYS} days of {SIGNAL_ASSET} history', 'missing_tickers': [SIGNAL_ASSET]}

    trend = float(spy.iloc[-1]) / float(spy.iloc[-SMA_DAYS:].mean()) - 1.0
    timing_asset = OFFENSIVE_ASSET if trend > 0 else DEFENSIVE_ASSET

    weights: Dict[str, float] = {}
    for t in FIXED_ASSETS + [timing_asset]:
        weights[t] = weights.get(t, 0.0) + 0.25

    missing = [t for t in weights if t not in history.columns or history[t].dropna().empty]
    result = {
        'allocation_weights': weights,
        'selected_asset': timing_asset,
        'momentum_scores': {SIGNAL_ASSET: round(trend, 6)},
    }
    if missing:
        result['missing_tickers'] = missing
    return result


class LAAStrategy(BaseStrategy):
    """Lethargic Asset Allocation by Wouter Keller (simplified, price signal only)."""

    def __init__(self):
        super().__init__(
            name="LAA (Lethargic Asset Allocation)",
            description=(
                "Keeps 75% fixed in value stocks (IWD), gold (GLD) and Treasuries (IEF). "
                "The last 25% holds Nasdaq (QQQ) while the S&P 500 is above its 200-day average, "
                "otherwise short-term Treasuries (SHY). Simplified: no unemployment signal."
            ),
        )

    def calculate_plan(self, **kwargs) -> Dict:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=420)
        try:
            prices, failed = get_price_repository().get_close_prices(UNIVERSE, start_date, end_date)
        except Exception as e:
            return {'error': f'Failed to download data: {str(e)}'}
        if prices is None or prices.empty:
            return {'error': 'No price data available', 'missing_tickers': failed}

        result = compute_laa(prices.sort_index())
        if 'error' in result:
            return result
        result['date'] = end_date.strftime('%Y-%m-%d')
        all_missing = sorted(set(failed + result.get('missing_tickers', [])))
        if all_missing:
            result['missing_tickers'] = all_missing
        return result

    def get_parameters(self) -> List[Dict]:
        return []

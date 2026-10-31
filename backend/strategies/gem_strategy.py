from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd

from .base_strategy import BaseStrategy
from market import get_price_repository

US_EQUITY = "SPY"
INTL_EQUITY = "EFA"
BOND = "AGG"
CASH = "BIL"
UNIVERSE = [US_EQUITY, INTL_EQUITY, BOND, CASH]
DEFAULT_LOOKBACK_MONTHS = 12


def _series_return(close: pd.Series, trading_days: int):
    close = close.dropna()
    if len(close) <= trading_days:
        return None
    return float(close.iloc[-1] / close.iloc[-(trading_days + 1)] - 1.0)


def compute_gem(history: pd.DataFrame, lookback_months: int = DEFAULT_LOOKBACK_MONTHS) -> Dict:
    """
    Pure GEM decision as of the last row of `history` (daily close prices).

    Absolute momentum: if US stocks beat cash (BIL) over the lookback, hold
    stocks; otherwise hold bonds (AGG).
    Relative momentum: among stocks, hold the stronger of US (SPY) and
    international (EFA). Ties go to SPY.
    """
    trading_days = int(lookback_months) * 21

    returns: Dict[str, float] = {}
    for t in UNIVERSE:
        if history is None or t not in history.columns:
            continue
        r = _series_return(history[t], trading_days)
        if r is not None:
            returns[t] = round(r, 6)

    missing = [t for t in UNIVERSE if t not in returns]
    if US_EQUITY in missing or CASH in missing:
        return {'error': f'Not enough price history for {US_EQUITY}/{CASH}', 'missing_tickers': missing}

    if returns[US_EQUITY] > returns[CASH]:
        if INTL_EQUITY in returns and returns[INTL_EQUITY] > returns[US_EQUITY]:
            selected = INTL_EQUITY
        else:
            selected = US_EQUITY
    else:
        selected = BOND if BOND in returns else CASH

    result = {
        'allocation_weights': {selected: 1.0},
        'selected_asset': selected,
        'momentum_scores': returns,
    }
    if missing:
        result['missing_tickers'] = missing
    return result


class GEMStrategy(BaseStrategy):
    """Global Equities Momentum (Gary Antonacci's dual momentum)."""

    def __init__(self):
        super().__init__(
            name="GEM (Dual Momentum)",
            description=(
                "Holds one asset at a time: the stronger of US (SPY) and international (EFA) stocks "
                "when US stocks beat cash (BIL) over 12 months, otherwise bonds (AGG)."
            ),
        )

    def calculate_plan(self, **kwargs) -> Dict:
        try:
            lookback_months = max(1, min(12, int(float(kwargs.get('lookback_months', DEFAULT_LOOKBACK_MONTHS)))))
        except Exception:
            return {'error': 'lookback_months must be a number between 1 and 12'}

        end_date = datetime.today()
        start_date = end_date - timedelta(days=420)
        try:
            prices, failed = get_price_repository().get_close_prices(UNIVERSE, start_date, end_date)
        except Exception as e:
            return {'error': f'Failed to download data: {str(e)}'}
        if prices is None or prices.empty:
            return {'error': 'No price data available', 'missing_tickers': failed}

        result = compute_gem(prices.sort_index(), lookback_months)
        if 'error' in result:
            return result
        result['date'] = end_date.strftime('%Y-%m-%d')
        return result

    def get_parameters(self) -> List[Dict]:
        return [
            {
                'name': 'lookback_months',
                'label': 'Lookback Months',
                'type': 'number',
                'default': DEFAULT_LOOKBACK_MONTHS,
                'min': 1,
                'max': 12,
                'description': 'Momentum lookback window in months (12 in the original strategy)',
            },
        ]

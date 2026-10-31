from datetime import datetime, timedelta
from typing import Dict, List, Union

import pandas as pd

from .base_strategy import BaseStrategy
from market import get_price_repository

DEFAULT_RISK_ASSETS = ["SPY", "EFA", "IEF", "DBC", "VNQ"]
DEFAULT_CASH_ASSET = "BIL"
DEFAULT_SMA_MONTHS = 10


def normalize_tickers(value: Union[str, List[str]]) -> List[str]:
    if isinstance(value, str):
        parts = value.split(',')
    elif isinstance(value, list):
        parts = value
    else:
        return []
    return list(dict.fromkeys(str(p).strip().upper() for p in parts if str(p).strip()))


def compute_gtaa(
    history: pd.DataFrame,
    risk_assets: List[str],
    cash_asset: str = DEFAULT_CASH_ASSET,
    sma_months: int = DEFAULT_SMA_MONTHS,
) -> Dict:
    """
    Pure GTAA decision as of the last row of `history` (daily close prices).

    Each risk asset gets an equal slice. A slice holds its asset while the
    latest price is above the average of the last `sma_months` month-end
    prices (the current month's latest price counts as its month-end), and
    moves to cash otherwise.
    """
    if not risk_assets:
        return {'error': 'No risk assets given'}

    trends: Dict[str, float] = {}
    missing: List[str] = []
    for t in risk_assets:
        if history is None or t not in history.columns:
            missing.append(t)
            continue
        close = history[t].dropna()
        monthly = close.groupby(close.index.to_period('M')).tail(1)
        if len(monthly) < sma_months:
            missing.append(t)
            continue
        sma = float(monthly.iloc[-sma_months:].mean())
        trends[t] = round(float(close.iloc[-1]) / sma - 1.0, 6)

    if not trends:
        return {'error': 'Not enough price history for any risk asset', 'missing_tickers': missing}

    # Missing assets keep their slice in cash so the other slices stay 1/N.
    each = 1.0 / len(risk_assets)
    weights: Dict[str, float] = {}
    invested: List[str] = []
    for t in risk_assets:
        target = t if trends.get(t, -1.0) > 0 else cash_asset
        if target == t:
            invested.append(t)
        weights[target] = round(weights.get(target, 0.0) + each, 6)

    result = {
        'allocation_weights': weights,
        'momentum_scores': trends,
        'offensive_ratio': round(len(invested) / len(risk_assets), 4),
        'selected_offensive': invested,
    }
    if missing:
        result['missing_tickers'] = missing
    return result


class GTAAStrategy(BaseStrategy):
    """Mebane Faber's GTAA (timing model from 'A Quantitative Approach to Tactical Asset Allocation')."""

    def __init__(self):
        super().__init__(
            name="GTAA (Faber Trend Following)",
            description=(
                "Splits money equally across five asset classes and holds each one only while it trades "
                "above its 10-month moving average; otherwise that slice goes to cash (BIL)."
            ),
        )

    def calculate_plan(self, **kwargs) -> Dict:
        risk_assets = normalize_tickers(kwargs.get('risk_assets', DEFAULT_RISK_ASSETS)) or list(DEFAULT_RISK_ASSETS)
        try:
            sma_months = max(2, min(12, int(float(kwargs.get('sma_months', DEFAULT_SMA_MONTHS)))))
        except Exception:
            return {'error': 'sma_months must be a number between 2 and 12'}

        end_date = datetime.today()
        start_date = end_date - timedelta(days=420)
        tickers = list(dict.fromkeys(risk_assets + [DEFAULT_CASH_ASSET]))
        try:
            prices, failed = get_price_repository().get_close_prices(tickers, start_date, end_date)
        except Exception as e:
            return {'error': f'Failed to download data: {str(e)}'}
        if prices is None or prices.empty:
            return {'error': 'No price data available', 'missing_tickers': failed}

        result = compute_gtaa(prices.sort_index(), risk_assets, DEFAULT_CASH_ASSET, sma_months)
        if 'error' in result:
            return result
        result['date'] = end_date.strftime('%Y-%m-%d')
        all_missing = sorted(set(failed + result.get('missing_tickers', [])))
        if all_missing:
            result['missing_tickers'] = all_missing
        return result

    def get_parameters(self) -> List[Dict]:
        return [
            {
                'name': 'risk_assets',
                'label': 'Risk Assets',
                'type': 'text',
                'default': ','.join(DEFAULT_RISK_ASSETS),
                'description': 'Comma-separated tickers, each gets an equal slice (US stocks, intl stocks, bonds, commodities, REITs)',
            },
            {
                'name': 'sma_months',
                'label': 'Moving Average Months',
                'type': 'number',
                'default': DEFAULT_SMA_MONTHS,
                'min': 2,
                'max': 12,
                'description': 'Trend filter length in months (10 in the original strategy)',
            },
        ]

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Union

from .base_strategy import BaseStrategy
from market import get_price_repository


class DAAStrategy(BaseStrategy):
    """
    DAA (Defensive Asset Allocation) by Wouter Keller.

    Canary assets (VWO, BND) determine the offensive/defensive split:
      - Both positive  → 100% offensive
      - One positive   → 50% offensive / 50% defensive
      - Both negative  → 0% offensive / 100% defensive

    Offensive portion: top N of 12 ETFs by momentum score, equal-weight.
    Defensive portion: single best defensive asset by momentum score.

    Momentum score = 12*R1 + 4*R3 + 2*R6 + 1*R12
    """

    def __init__(self):
        super().__init__(
            name="DAA (Defensive Asset Allocation)",
            description=(
                "Uses canary assets (VWO, BND) to gauge market breadth. "
                "Allocates equally to the top N offensive ETFs when markets are healthy, "
                "and shifts to the best defensive bond during downturns."
            ),
        )
        self.default_offensive = [
            'SPY', 'QQQ', 'IWM', 'VGK', 'EWJ', 'EEM',
            'VNQ', 'GLD', 'DBC', 'HYG', 'LQD', 'TLT',
        ]
        self.default_defensive = ['LQD', 'IEF', 'SHY']
        self.default_canary = ['VWO', 'BND']
        self.default_top_n = 6

        self.lookbacks = {"R1": 21, "R3": 63, "R6": 126, "R12": 252}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalize_tickers(self, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            parts = value.split(',')
        else:
            parts = list(value)
        return [str(p).strip().upper() for p in parts if str(p).strip()]

    def _series_return(self, close: pd.Series, trading_days: int):
        close = close.dropna()
        if len(close) <= trading_days:
            return None
        return float(close.iloc[-1] / close.iloc[-(trading_days + 1)] - 1.0)

    def _momentum_score(self, close: pd.Series):
        r1  = self._series_return(close, self.lookbacks["R1"])
        r3  = self._series_return(close, self.lookbacks["R3"])
        r6  = self._series_return(close, self.lookbacks["R6"])
        r12 = self._series_return(close, self.lookbacks["R12"])
        if any(v is None for v in [r1, r3, r6, r12]):
            return None
        return 12 * r1 + 4 * r3 + 2 * r6 + 1 * r12

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def calculate_plan(self, **kwargs) -> Dict:
        offensive = self._normalize_tickers(kwargs.get('offensive_assets', self.default_offensive))
        defensive = self._normalize_tickers(kwargs.get('defensive_assets', self.default_defensive))
        canary    = self._normalize_tickers(kwargs.get('canary_assets',    self.default_canary))
        top_n     = int(kwargs.get('top_n', self.default_top_n))

        all_tickers = list(dict.fromkeys(offensive + defensive + canary))

        end_date   = datetime.today()
        start_date = end_date - timedelta(days=420)

        try:
            repo = get_price_repository()
            price_data, failed = repo.get_close_prices(all_tickers, start_date, end_date)
            price_data = price_data.dropna(axis=1, how='all')
        except Exception as e:
            return {'error': f'Failed to download data: {str(e)}'}

        if price_data.empty:
            return {'error': 'No price data available', 'missing_tickers': failed}

        # Score all tickers
        scores: Dict[str, float] = {}
        missing_for_calc: List[str] = []
        for t in all_tickers:
            if t not in price_data.columns:
                missing_for_calc.append(t)
                continue
            s = self._momentum_score(price_data[t])
            if s is None:
                missing_for_calc.append(t)
                continue
            scores[t] = round(float(s), 6)

        # Canary signal
        scored_canary = [t for t in canary if t in scores]
        if not scored_canary:
            return {
                'error': 'No canary asset data available',
                'missing_tickers': sorted(set(failed + missing_for_calc)),
            }
        positive_count = sum(1 for t in scored_canary if scores[t] >= 0)
        offensive_ratio = positive_count / len(scored_canary)
        defensive_ratio = 1.0 - offensive_ratio

        # Build weights
        weights: Dict[str, float] = {}

        scored_offensive = [t for t in offensive if t in scores]
        selected_offensive: List[str] = []
        if offensive_ratio > 0 and scored_offensive:
            effective_n = min(top_n, len(scored_offensive))
            selected_offensive = sorted(scored_offensive, key=lambda t: scores[t], reverse=True)[:effective_n]
            each = offensive_ratio / effective_n
            for t in selected_offensive:
                weights[t] = round(weights.get(t, 0.0) + each, 6)

        scored_defensive = [t for t in defensive if t in scores]
        if defensive_ratio > 0 and scored_defensive:
            best_def = max(scored_defensive, key=lambda t: scores[t])
            weights[best_def] = round(weights.get(best_def, 0.0) + defensive_ratio, 6)

        if not weights:
            return {
                'error': 'Could not compute allocation weights',
                'missing_tickers': sorted(set(failed + missing_for_calc)),
            }

        result = {
            'date': end_date.strftime('%Y-%m-%d'),
            'allocation_weights': weights,
            'offensive_ratio': round(offensive_ratio, 4),
            'defensive_ratio': round(defensive_ratio, 4),
            'canary_scores': {t: scores[t] for t in scored_canary},
            'positive_canary_count': positive_count,
            'total_canary_count': len(scored_canary),
            'momentum_scores': scores,
            'selected_offensive': selected_offensive,
        }

        all_missing = sorted(set(failed + missing_for_calc))
        if all_missing:
            result['missing_tickers'] = all_missing

        return result

    # ------------------------------------------------------------------
    # UI parameters
    # ------------------------------------------------------------------

    def get_parameters(self) -> List[Dict]:
        return [
            {
                'name': 'offensive_assets',
                'label': 'Offensive Assets',
                'type': 'text',
                'default': ','.join(self.default_offensive),
                'description': 'Comma-separated tickers for offensive ETFs (12 ETFs by default)',
            },
            {
                'name': 'defensive_assets',
                'label': 'Defensive Assets',
                'type': 'text',
                'default': ','.join(self.default_defensive),
                'description': 'Comma-separated tickers for defensive assets (e.g. LQD,IEF,SHY)',
            },
            {
                'name': 'canary_assets',
                'label': 'Canary Assets',
                'type': 'text',
                'default': ','.join(self.default_canary),
                'description': 'Market breadth signal tickers (e.g. VWO,BND)',
            },
            {
                'name': 'top_n',
                'label': 'Top N Offensive ETFs',
                'type': 'number',
                'default': self.default_top_n,
                'min': 1,
                'max': 12,
                'description': 'Number of top offensive ETFs to invest in equally',
            },
        ]

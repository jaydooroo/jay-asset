import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
from .base_strategy import BaseStrategy
from market import get_price_repository

class PAAStrategy(BaseStrategy):
    """Protective Asset Allocation Strategy"""

    def __init__(self):
        super().__init__(
            name="PAA (Protective Asset Allocation)",
            description=(
                "Ranks ETFs by 12-month momentum and allocates to the top performers. "
                "If momentum is weak, shifts a portion into defensive bonds (IEF)."
            )
        )
        self.default_etfs = ['SPY', 'QQQ', 'IWM', 'VGK', 'EWJ', 'EEM', 'VNQ', 'GLD', 'DBC', 'HYG', 'LQD']
        self.fallback_asset = 'IEF'

    @staticmethod
    def _normalize_tickers(value) -> list:
        """Accept "SPY,QQQ" (form text) or ["SPY", "QQQ"]; return uppercase tickers."""
        parts = value.split(',') if isinstance(value, str) else (value or [])
        return [str(p).strip().upper() for p in parts if str(p).strip()]

    def calculate_ief_ratio(self, num_negative_momentum: int) -> float:
        """Calculate defensive asset ratio based on negative momentum count"""
        lookup = {
            0: 0.0,
            1: 1/6,
            2: 2/6,
            3: 3/6,
            4: 4/6,
            5: 5/6,
            6: 1.0
        }
        return lookup.get(num_negative_momentum, 1.0)

    def calculate_plan(self, **kwargs) -> Dict:
        """
        Calculate PAA allocation weights (independent of investment amount).

        Args:
            etfs: List of ETF tickers (optional)
            top_n: Number of top ETFs to select (default: 6)
            lookback_months: Lookback period in months (default: 12)

        Returns:
            Dictionary with allocation plan details (weights + metadata)
        """
        etfs = self._normalize_tickers(kwargs.get('etfs', self.default_etfs)) or list(self.default_etfs)
        try:
            top_n = max(1, int(float(kwargs.get('top_n', 6))))
            lookback_months = max(1, int(float(kwargs.get('lookback_months', 12))))
        except (TypeError, ValueError):
            return {'error': 'top_n and lookback_months must be numbers'}

        # Momentum compares the price with its average over the lookback
        # (12 months = 252 trading days). Download enough calendar days to
        # cover that many trading days, plus a margin for holidays.
        window = lookback_months * 21
        all_tickers = list(dict.fromkeys(etfs + [self.fallback_asset]))
        end_date = datetime.today()
        start_date = end_date - timedelta(days=int(window * 365 / 252) + 45)

        try:
            price_repository = get_price_repository()
            price_data, failed_tickers = price_repository.get_close_prices(all_tickers, start_date, end_date)

            # Drop columns with all NaN values
            price_data = price_data.dropna(axis=1, how='all')

            # Check if we have enough data
            if price_data.empty:
                return {
                    'error': (
                        'No stored price data was found for these tickers. '
                        'Add them to MARKET_INGEST_TICKERS and backfill them from Tiingo.'
                    ),
                    'missing_tickers': failed_tickers or list(all_tickers),
                }

            if len(price_data) < window:
                return {'error': f'Insufficient data: need at least {window} days, got {len(price_data)} days'}

        except Exception as e:
            return {'error': f'Failed to download data: {str(e)}'}

        # Simple moving average over the lookback window
        rolling_avg = price_data.rolling(window=window).mean().iloc[-1]
        current_price = price_data.iloc[-1]
        momentum = (current_price / rolling_avg) - 1
        momentum = momentum.dropna()

        if momentum.empty:
            return {'error': 'Unable to calculate momentum - insufficient data'}

        # Filter to only ETFs that we have data for
        available_etfs = [etf for etf in etfs if etf in momentum.index]
        if len(available_etfs) == 0:
            return {'error': f'No price data available for any of the requested ETFs'}

        if top_n > len(available_etfs):
            top_n = len(available_etfs)

        # Select top N ETFs by momentum
        selected = momentum[available_etfs].sort_values(ascending=False).head(top_n)
        num_negative = (momentum[available_etfs] < 0).sum()
        ief_ratio = self.calculate_ief_ratio(num_negative)
        offensive_ratio = 1 - ief_ratio
        avg_momentum = round(float(selected.mean()), 4) if not selected.empty else 0.0
        best_etf = selected.idxmax() if not selected.empty else None
        worst_etf = selected.idxmin() if not selected.empty else None

        # Calculate weights
        ief_weight = float(ief_ratio)
        offensive_weight_each = (1.0 - ief_weight) / float(top_n) if top_n != 0 else 0.0

        weights: Dict[str, float] = {}
        # Scores for every candidate ETF, not just the selected ones, so the UI
        # can show why the top N were picked.
        momentum_data = {etf: round(float(momentum[etf]), 4) for etf in available_etfs}

        # Allocate to offensive assets
        for etf in selected.index:
            if momentum[etf] >= 0:
                weights[etf] = float(offensive_weight_each)

        # Add defensive allocation weight
        if ief_weight > 0:
            weights[self.fallback_asset] = float(ief_weight)

        result = {
            'date': datetime.today().strftime("%Y-%m-%d"),
            'allocation_weights': weights,
            'defensive_ratio': round(ief_ratio, 4),
            'offensive_ratio': round(offensive_ratio, 4),
            'num_negative_momentum': int(num_negative),
            'momentum_scores': momentum_data,
            'selected_etfs': list(selected.index),
            'avg_momentum': avg_momentum,
            'best_etf': best_etf,
            'worst_etf': worst_etf
        }
        if 'failed_tickers' in locals() and failed_tickers:
            result['missing_tickers'] = failed_tickers
        return result

    def get_parameters(self):
        """Get UI parameters for this strategy"""
        return [
            {
                'name': 'etfs',
                'label': 'ETF Tickers',
                'type': 'text',
                'default': ','.join(self.default_etfs),
                'description': 'Comma-separated list of ETF tickers'
            },
            {
                'name': 'top_n',
                'label': 'Top N ETFs',
                'type': 'number',
                'default': 6,
                'min': 1,
                'max': 12,
                'description': 'Number of top-performing ETFs to select'
            },
            {
                'name': 'lookback_months',
                'label': 'Lookback Period (Months)',
                'type': 'number',
                'default': 12,
                'min': 6,
                'max': 24,
                'description': 'Historical period for momentum calculation'
            }
        ]

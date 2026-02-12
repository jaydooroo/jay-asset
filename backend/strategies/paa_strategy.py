import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
from .base_strategy import BaseStrategy
from market_data import download_close_prices

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
        etfs = kwargs.get('etfs', self.default_etfs)
        top_n = kwargs.get('top_n', 6)
        lookback_months = kwargs.get('lookback_months', 12)

        all_tickers = etfs + [self.fallback_asset]
        end_date = datetime.today()
        start_date = end_date - timedelta(days=lookback_months * 30 + 30)

        try:
            price_data, failed_tickers = download_close_prices(all_tickers, start_date, end_date)

            # Drop columns with all NaN values
            price_data = price_data.dropna(axis=1, how='all')

            # Check if we have enough data
            if price_data.empty:
                return {'error': 'No valid price data after cleaning'}

            if len(price_data) < 252:
                return {'error': f'Insufficient data: need at least 252 days, got {len(price_data)} days'}

        except Exception as e:
            return {'error': f'Failed to download data: {str(e)}'}

        # Calculate 12-month simple moving average
        rolling_avg = price_data.rolling(window=252).mean().iloc[-1]
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
        momentum_data = {}

        # Allocate to offensive assets
        for etf in selected.index:
            if momentum[etf] >= 0:
                weights[etf] = float(offensive_weight_each)
            momentum_data[etf] = round(float(momentum[etf]), 4)

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

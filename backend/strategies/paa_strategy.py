import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict
from .base_strategy import BaseStrategy

class PAAStrategy(BaseStrategy):
    """Protective Asset Allocation Strategy"""

    def __init__(self):
        super().__init__(
            name="PAA (Protective Asset Allocation)",
            description="Momentum-based strategy with defensive asset protection"
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

    def calculate_allocation(self, total_money: float, **kwargs) -> Dict:
        """
        Calculate PAA allocation

        Args:
            total_money: Total amount to allocate
            etfs: List of ETF tickers (optional)
            top_n: Number of top ETFs to select (default: 6)
            lookback_months: Lookback period in months (default: 12)

        Returns:
            Dictionary with allocation details
        """
        etfs = kwargs.get('etfs', self.default_etfs)
        top_n = kwargs.get('top_n', 6)
        lookback_months = kwargs.get('lookback_months', 12)

        all_tickers = etfs + [self.fallback_asset]
        end_date = datetime.today()
        start_date = end_date - timedelta(days=lookback_months * 30 + 30)

        try:
            # Try a single batch download first (faster, fewer Yahoo requests)
            import time
            failed_tickers = []
            batch_data = yf.download(
                all_tickers,
                start=start_date,
                end=end_date,
                progress=False,
                threads=False,
                ignore_tz=True
            )

            if batch_data is not None and not batch_data.empty:
                if isinstance(batch_data.columns, pd.MultiIndex):
                    if 'Close' in batch_data.columns.levels[0]:
                        price_data = batch_data['Close']
                    else:
                        price_data = pd.DataFrame()
                else:
                    if 'Close' in batch_data.columns:
                        price_data = batch_data[['Close']]
                        price_data.columns = [all_tickers[0]]
                    else:
                        price_data = batch_data
            else:
                price_data = pd.DataFrame()

            # If batch fails or is empty, fall back to per-ticker with retries
            if price_data.empty:
                series_by_ticker = {}
                max_retries = 3

                for ticker in all_tickers:
                    data = None
                    for attempt in range(max_retries):
                        try:
                            data = yf.download(
                                ticker,
                                start=start_date,
                                end=end_date,
                                progress=False,
                                threads=False,
                                ignore_tz=True
                            )

                            if data is not None and not data.empty:
                                break

                            if attempt < max_retries - 1:
                                time.sleep(2)
                        except Exception:
                            if attempt < max_retries - 1:
                                time.sleep(2)

                    if data is None or data.empty:
                        failed_tickers.append(ticker)
                        continue

                    if isinstance(data.columns, pd.MultiIndex):
                        if 'Close' in data.columns.levels[0]:
                            series = data['Close'].rename(ticker)
                        else:
                            failed_tickers.append(ticker)
                            continue
                    else:
                        if 'Close' in data.columns:
                            series = data['Close'].rename(ticker)
                        else:
                            series = data.squeeze()
                            series.name = ticker

                    series_by_ticker[ticker] = series

                if not series_by_ticker:
                    return {
                        'error': 'Failed to download price data. Yahoo Finance may be temporarily unavailable.',
                        'failed_tickers': failed_tickers
                    }

                price_data = pd.concat(series_by_ticker.values(), axis=1)

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

        # Calculate allocations
        ief_amount = round(total_money * ief_ratio, 2)
        remaining_amount = total_money - ief_amount
        offensive_allocation = round(remaining_amount / top_n, 2) if top_n != 0 else 0

        allocation = {}
        momentum_data = {}

        # Allocate to offensive assets
        for etf in selected.index:
            if momentum[etf] >= 0:
                allocation[etf] = offensive_allocation
            momentum_data[etf] = round(float(momentum[etf]), 4)

        # Add defensive allocation
        if ief_amount > 0:
            allocation[self.fallback_asset] = ief_amount

        result = {
            'strategy': self.name,
            'date': datetime.today().strftime("%Y-%m-%d"),
            'total_amount': total_money,
            'allocation': allocation,
            'defensive_ratio': round(ief_ratio, 4),
            'offensive_ratio': round(offensive_ratio, 4),
            'num_negative_momentum': int(num_negative),
            'momentum_scores': momentum_data,
            'selected_etfs': list(selected.index)
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

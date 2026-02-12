from datetime import datetime
from typing import Dict
from .base_strategy import BaseStrategy

class SimpleMomentumStrategy(BaseStrategy):
    """Simple Momentum Strategy (Demo without external API)"""

    def __init__(self):
        super().__init__(
            name="Simple Momentum (Demo)",
            description="Momentum-based strategy with simulated data for testing"
        )

    def calculate_plan(self, **kwargs) -> Dict:
        """
        Calculate allocation weights based on simulated momentum.

        This is a demo strategy that doesn't require external APIs.
        In production, you would replace this with real market data.
        """
        # This dictionary maps asset ticker -> momentum score.
        # Higher momentum means we prefer that asset.
        # Simulated momentum scores
        assets = {
            'SPY': 0.12,   # S&P 500 - positive momentum
            'QQQ': 0.18,   # NASDAQ - strong positive momentum
            'IWM': -0.05,  # Small caps - slightly negative
            'VGK': 0.08,   # Europe - moderate positive
            'EEM': -0.03,  # Emerging markets - slightly negative
            'IEF': 0.04,   # Bonds - defensive, slight positive
        }

        # Sort by momentum (highest first).
        sorted_assets = sorted(assets.items(), key=lambda x: x[1], reverse=True)

        # Take top 3 assets that have positive momentum.
        # If momentum <= 0, we avoid allocating to it.
        top_assets = [(asset, momentum) for asset, momentum in sorted_assets if momentum > 0][:3]

        if not top_assets:
            # All negative momentum - allocate to defensive (IEF)
            weights = {'IEF': 1.0}
            selected_assets = ['IEF']
            note = 'All assets showing negative momentum - 100% defensive allocation'
        else:
            # Equal weight allocation across the selected assets.
            per = 1.0 / len(top_assets)
            weights = {asset: per for asset, _ in top_assets}
            selected_assets = [asset for asset, _ in top_assets]
            note = 'This is a demo with simulated data. Connect to real data sources for production use.'

        # Create momentum scores for display (rounded for nicer UI output).
        momentum_scores = {asset: round(momentum, 4) for asset, momentum in assets.items()}

        return {
            'date': datetime.today().strftime("%Y-%m-%d"),
            'allocation_weights': weights,
            'momentum_scores': momentum_scores,
            'selected_assets': selected_assets,
            'note': note,
        }

    def get_parameters(self):
        """Get UI parameters for this strategy"""
        return []

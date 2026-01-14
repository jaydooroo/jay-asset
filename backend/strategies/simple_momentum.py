from typing import Dict
from .base_strategy import BaseStrategy
import random

class SimpleMomentumStrategy(BaseStrategy):
    """Simple Momentum Strategy (Demo without external API)"""

    def __init__(self):
        super().__init__(
            name="Simple Momentum (Demo)",
            description="Momentum-based strategy with simulated data for testing"
        )

    def calculate_allocation(self, total_money: float, **kwargs) -> Dict:
        """
        Calculate allocation based on simulated momentum

        This is a demo strategy that doesn't require external APIs.
        In production, you would replace this with real market data.
        """
        # Simulated momentum scores
        assets = {
            'SPY': 0.12,   # S&P 500 - positive momentum
            'QQQ': 0.18,   # NASDAQ - strong positive momentum
            'IWM': -0.05,  # Small caps - slightly negative
            'VGK': 0.08,   # Europe - moderate positive
            'EEM': -0.03,  # Emerging markets - slightly negative
            'IEF': 0.04,   # Bonds - defensive, slight positive
        }

        # Sort by momentum
        sorted_assets = sorted(assets.items(), key=lambda x: x[1], reverse=True)

        # Take top 3 with positive momentum
        top_assets = [(asset, momentum) for asset, momentum in sorted_assets if momentum > 0][:3]

        if not top_assets:
            # All negative momentum - allocate to defensive (IEF)
            return {
                'strategy': self.name,
                'allocation': {'IEF': total_money},
                'total_amount': total_money,
                'note': 'All assets showing negative momentum - 100% defensive allocation'
            }

        # Equal weight allocation to top assets
        allocation_per_asset = total_money / len(top_assets)

        allocation = {}
        for asset, momentum in top_assets:
            allocation[asset] = round(allocation_per_asset, 2)

        # Create momentum scores for display
        momentum_scores = {asset: round(momentum, 4) for asset, momentum in assets.items()}

        return {
            'strategy': self.name,
            'allocation': allocation,
            'total_amount': total_money,
            'momentum_scores': momentum_scores,
            'selected_assets': [asset for asset, _ in top_assets],
            'note': 'This is a demo with simulated data. Connect to real data sources for production use.'
        }

    def get_parameters(self):
        """Get UI parameters for this strategy"""
        return []

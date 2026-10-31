from typing import Dict, List, Union

from .base_strategy import BaseStrategy


def parse_weights(value: Union[str, Dict, None]) -> Dict[str, float]:
    """
    Parse target weights from "SPY:60,AGG:40" or {"SPY": 60, "AGG": 40}.

    Returns uppercase tickers with weights normalized to sum to 1.0, or {} if
    nothing valid was given. Repeated tickers are added together.
    """
    if isinstance(value, dict):
        pairs = list(value.items())
    elif isinstance(value, str):
        pairs = []
        for part in value.split(","):
            if ":" not in part:
                continue
            ticker, weight = part.split(":", 1)
            pairs.append((ticker, weight))
    else:
        return {}

    raw: Dict[str, float] = {}
    for ticker, weight in pairs:
        ticker = str(ticker).strip().upper()
        try:
            w = float(str(weight).strip().rstrip("%"))
        except Exception:
            continue
        if not ticker or w <= 0:
            continue
        raw[ticker] = raw.get(ticker, 0.0) + w

    total = sum(raw.values())
    if total <= 0:
        return {}
    return {ticker: round(w / total, 6) for ticker, w in sorted(raw.items())}


def format_weights(weights: Dict[str, float]) -> str:
    """Format weights as "SPY:60,AGG:40" (percent) for UI defaults."""
    return ",".join(f"{ticker}:{round(w * 100, 2):g}" for ticker, w in weights.items())


class StaticAllocationStrategy(BaseStrategy):
    """
    Fixed-weight portfolio (60/40, Permanent, All Weather, ...).

    No price data is needed: the plan is just the target weights. Investors
    typically rebalance back to these weights once a year.
    """

    category = "static"

    def __init__(self, name: str, description: str, default_weights: Dict[str, float]):
        super().__init__(name=name, description=description)
        self.default_weights = parse_weights(default_weights)

    def calculate_plan(self, **kwargs) -> Dict:
        if "weights" in kwargs:
            weights = parse_weights(kwargs["weights"])
            if not weights:
                return {'error': 'Invalid weights. Use TICKER:WEIGHT pairs, e.g. SPY:60,AGG:40'}
        else:
            weights = dict(self.default_weights)

        return {
            'allocation_weights': weights,
            'rebalance': 'annual',
        }

    def get_parameters(self) -> List[Dict]:
        return [
            {
                'name': 'weights',
                'label': 'Target Weights',
                'type': 'text',
                'default': format_weights(self.default_weights),
                'description': 'Comma-separated TICKER:WEIGHT pairs (normalized to 100%)',
            },
        ]


STATIC_PORTFOLIOS = {
    'sixty_forty': {
        'name': '60/40 Portfolio',
        'description': 'Classic balanced portfolio: 60% US stocks, 40% US bonds.',
        'weights': {'SPY': 60, 'AGG': 40},
    },
    'permanent': {
        'name': 'Permanent Portfolio',
        'description': "Harry Browne's portfolio: equal parts stocks, long-term Treasuries, gold, and cash.",
        'weights': {'SPY': 25, 'TLT': 25, 'GLD': 25, 'BIL': 25},
    },
    'all_weather': {
        'name': 'All Weather Portfolio',
        'description': (
            "Simplified version of Ray Dalio's risk-balanced portfolio: "
            "30% stocks, 55% Treasuries, 7.5% gold, 7.5% commodities."
        ),
        'weights': {'SPY': 30, 'TLT': 40, 'IEF': 15, 'GLD': 7.5, 'DBC': 7.5},
    },
    'golden_butterfly': {
        'name': 'Golden Butterfly',
        'description': (
            'Equal parts large-cap stocks, small-cap value stocks, long-term Treasuries, '
            'short-term Treasuries, and gold.'
        ),
        'weights': {'SPY': 20, 'VBR': 20, 'TLT': 20, 'SHY': 20, 'GLD': 20},
    },
}


def build_static_strategies() -> Dict[str, StaticAllocationStrategy]:
    return {
        strategy_id: StaticAllocationStrategy(p['name'], p['description'], p['weights'])
        for strategy_id, p in STATIC_PORTFOLIOS.items()
    }

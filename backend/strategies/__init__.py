
from .paa_strategy import PAAStrategy
from .simple_momentum import SimpleMomentumStrategy
from .vaa_strategy import VAAStrategy

# Registry of all available strategies
STRATEGIES = {
    'paa': PAAStrategy(),
    'simple_momentum': SimpleMomentumStrategy(),
    'vaa': VAAStrategy()
}

def get_strategy(strategy_id: str):
    """Get strategy instance by ID"""
    return STRATEGIES.get(strategy_id)

def list_strategies():
    """Get list of all available strategies"""
    return {
        strategy_id: strategy.to_dict()
        for strategy_id, strategy in STRATEGIES.items()
    }

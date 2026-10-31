
from .paa_strategy import PAAStrategy
from .vaa_strategy import VAAStrategy
from .cdm_strategy import CDMStrategy
from .daa_strategy import DAAStrategy
from .gem_strategy import GEMStrategy
from .gtaa_strategy import GTAAStrategy
from .laa_strategy import LAAStrategy
from .static_allocation import build_static_strategies

# Registry of all available strategies
# If you add a new entry, also follow backend/NEW_STRATEGY_CHECKLIST.md.
STRATEGIES = {
    'paa': PAAStrategy(),
    'vaa': VAAStrategy(),
    'cdm': CDMStrategy(),
    'daa': DAAStrategy(),
    'gem': GEMStrategy(),
    'gtaa': GTAAStrategy(),
    'laa': LAAStrategy(),
    # Fixed-weight portfolios: sixty_forty, permanent, all_weather, golden_butterfly
    **build_static_strategies(),
}

def get_strategy(strategy_id: str):
    """Get strategy instance by ID"""
    return STRATEGIES.get(strategy_id)

def list_strategy_ids():
    """Return available strategy IDs."""
    return list(STRATEGIES.keys())

def list_strategies():
    """Get list of all available strategies"""
    return {
        strategy_id: strategy.to_dict()
        for strategy_id, strategy in STRATEGIES.items()
    }

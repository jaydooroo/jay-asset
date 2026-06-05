from .paa import PAAPerformanceSpec
from .vaa import VAAPerformanceSpec
from .cdm import CDMPerformanceSpec

# Keep in sync with backend/strategies/__init__.py when strategy performance is supported.
# Checklist: backend/NEW_STRATEGY_CHECKLIST.md
SPECS = {
    "paa": PAAPerformanceSpec(),
    "vaa": VAAPerformanceSpec(),
    "cdm": CDMPerformanceSpec(),
}


def get_performance_spec(strategy_id: str):
    return SPECS.get(strategy_id)


def list_performance_spec_ids():
    return list(SPECS.keys())

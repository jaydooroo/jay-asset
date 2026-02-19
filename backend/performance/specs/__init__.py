from .paa import PAAPerformanceSpec
from .vaa import VAAPerformanceSpec

SPECS = {
    "paa": PAAPerformanceSpec(),
    "vaa": VAAPerformanceSpec(),
}


def get_performance_spec(strategy_id: str):
    return SPECS.get(strategy_id)


def list_performance_spec_ids():
    return list(SPECS.keys())


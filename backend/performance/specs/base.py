from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyPerformanceSpec:
    """
    Strategy specification for shared performance backtesting.

    Implementations should be pure:
    - No network I/O
    - No DynamoDB calls
    - Consume historical prices passed from the engine
    """

    strategy_id: str
    strategy_name: str
    strategy_version: str = "1"
    rebalance_frequency: str = "monthly"
    min_lookback_days: int = 252

    def default_parameters(self) -> dict:
        raise NotImplementedError

    def normalize_parameters(self, parameters: dict) -> dict:
        return dict(parameters or {})

    def universe(self, parameters: dict) -> list[str]:
        raise NotImplementedError

    def compute_weights(self, history, parameters: dict) -> dict:
        """
        Compute allocation weights as of the latest date in `history`.

        Args:
          history: pandas DataFrame of close prices indexed by date
          parameters: normalized strategy parameters

        Returns:
          dict with:
            - allocation_weights: Dict[ticker, weight]
          or:
            - error: str
        """
        raise NotImplementedError


from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseStrategy(ABC):
    """Base class for all investment strategies"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def calculate_plan(self, **kwargs) -> Dict[str, Any]:
        """
        Calculate the allocation plan independent of investment amount.

        Args:
            **kwargs: Strategy-specific parameters

        Returns:
            Dictionary containing at least:
              - allocation_weights: Dict[ticker, weight] (weights should sum to ~1.0)

            Additional strategy metadata (scores, selected assets, etc.) can also be included.
        """
        raise NotImplementedError

    @abstractmethod
    def get_parameters(self) -> List[Dict]:
        """
        Get strategy-specific parameters for the UI

        Returns:
            List of parameter definitions with name, type, default, etc.
        """
        pass

    def calculate_allocation(self, total_money: float, **kwargs) -> Dict[str, Any]:
        """
        Calculate a dollar allocation for a given investment amount.

        This default implementation uses `calculate_plan()` (weights) and scales it
        by `total_money`. Strategies can override this method if they need
        non-linear behavior, but most strategies should only implement
        `calculate_plan()`.
        """
        plan = self.calculate_plan(**kwargs)

        if not isinstance(plan, dict):
            return {"error": "Strategy returned invalid plan"}

        if "error" in plan:
            return plan

        weights = plan.get("allocation_weights")
        if not isinstance(weights, dict) or not weights:
            return {"error": "Strategy plan is missing allocation_weights"}

        allocation: Dict[str, float] = {}
        for ticker, weight in weights.items():
            try:
                w = float(weight)
            except Exception:
                continue
            if w <= 0:
                continue
            allocation[str(ticker)] = round(float(total_money) * w, 2)

        # Adjust rounding so the total matches total_money when possible.
        try:
            diff = round(float(total_money) - sum(allocation.values()), 2)
        except Exception:
            diff = 0.0

        if allocation and abs(diff) >= 0.01:
            # Add the rounding difference to the largest-weighted asset.
            try:
                best = max(allocation.keys(), key=lambda k: float(weights.get(k, 0.0)))
                allocation[best] = round(allocation[best] + diff, 2)
            except Exception:
                pass

        result: Dict[str, Any] = dict(plan)
        result["strategy"] = self.name
        result["total_amount"] = float(total_money)
        result["allocation_weights"] = weights
        result["allocation"] = allocation
        return result

    def to_dict(self) -> Dict:
        """
        Convert strategy info to a dictionary for the API response.

        The frontend uses this to:
        - populate the strategy dropdown (name/description)
        - render parameter input fields (parameters)
        """
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.get_parameters()
        }

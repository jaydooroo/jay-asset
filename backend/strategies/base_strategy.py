from abc import ABC, abstractmethod
from typing import Dict, List

class BaseStrategy(ABC):
    """Base class for all investment strategies"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def calculate_allocation(self, total_money: float, **kwargs) -> Dict[str, float]:
        """
        Calculate asset allocation based on strategy

        Args:
            total_money: Total amount to allocate
            **kwargs: Strategy-specific parameters

        Returns:
            Dictionary mapping asset names to dollar amounts
        """
        pass

    @abstractmethod
    def get_parameters(self) -> List[Dict]:
        """
        Get strategy-specific parameters for the UI

        Returns:
            List of parameter definitions with name, type, default, etc.
        """
        pass

    def to_dict(self) -> Dict:
        """Convert strategy info to dictionary for API response"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.get_parameters()
        }

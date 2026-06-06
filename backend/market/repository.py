from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, List, Tuple

import pandas as pd


class PriceRepository(ABC):
    """Interface for reading historical close prices."""

    @abstractmethod
    def get_close_prices(
        self,
        tickers: Iterable[str],
        start_date: datetime,
        end_date: datetime,
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Return daily close prices indexed by date with one column per ticker.

        Returns:
            price_data: DataFrame indexed by date, columns are ticker symbols.
            failed_tickers: tickers that could not be loaded by this repository.
        """
        raise NotImplementedError

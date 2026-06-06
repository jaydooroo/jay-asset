from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Tuple

import pandas as pd

from market_data import download_close_prices

from .repository import PriceRepository


class ExternalPriceRepository(PriceRepository):
    """
    Price repository backed by the current Stooq/Yahoo downloader.

    This class intentionally preserves today's behavior. It exists so strategy
    code no longer depends directly on the download implementation.
    """

    def get_close_prices(
        self,
        tickers: Iterable[str],
        start_date: datetime,
        end_date: datetime,
    ) -> Tuple[pd.DataFrame, List[str]]:
        return download_close_prices(tickers, start_date, end_date)

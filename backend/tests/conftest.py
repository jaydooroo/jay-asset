"""
Shared test setup.

Tests never touch DynamoDB or Tiingo: strategies read prices through
`FakePriceRepository` (helpers.py), installed with
`market.set_price_repository`, and the cache/performance tables are switched
off through their env flags.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
for path in (BACKEND_DIR, Path(__file__).resolve().parent):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import market  # noqa: E402
from helpers import FakePriceRepository  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch):
    """Keep every test away from AWS and from the developer's .env values."""
    monkeypatch.delenv("AWS_LAMBDA_FUNCTION_NAME", raising=False)
    monkeypatch.setenv("CACHE_ENABLED", "false")
    monkeypatch.setenv("PERFORMANCE_ENABLED", "false")
    for name in ("PERFORMANCE_BACKTEST_MONTHS", "PERFORMANCE_LOOKBACK_DAYS"):
        monkeypatch.delenv(name, raising=False)
    yield
    market.set_price_repository(None)


@pytest.fixture
def use_prices():
    """Install a FakePriceRepository: `repo = use_prices(frame)`."""

    def install(prices: pd.DataFrame) -> FakePriceRepository:
        repo = FakePriceRepository(prices)
        market.set_price_repository(repo)
        return repo

    return install

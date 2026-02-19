import os


def performance_enabled() -> bool:
    """Return whether performance snapshot features should run."""
    value = os.getenv("PERFORMANCE_ENABLED", "").strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def performance_table_name() -> str:
    """Return the DynamoDB table name for strategy performance snapshots."""
    return os.getenv("PERFORMANCE_TABLE", "jay-asset-performance")


def performance_ttl_seconds() -> int:
    """Return TTL for performance snapshots with safe fallback."""
    try:
        return int(os.getenv("PERFORMANCE_TTL_SECONDS", "5184000"))  # 60 days
    except ValueError:
        return 5184000


def performance_lookback_days() -> int:
    """Return minimum trading-day lookback window used by backtests."""
    try:
        return int(os.getenv("PERFORMANCE_LOOKBACK_DAYS", "252"))
    except ValueError:
        return 252


def performance_backtest_months() -> int:
    """Return how many recent monthly periods are used in walk-forward backtests."""
    try:
        return int(os.getenv("PERFORMANCE_BACKTEST_MONTHS", "12"))
    except ValueError:
        return 12

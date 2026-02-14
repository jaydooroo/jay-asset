import os


def cache_enabled() -> bool:
    """Return whether cache operations should run in this environment."""
    value = os.getenv("CACHE_ENABLED", "").strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def cache_table_name() -> str:
    """Return the DynamoDB table name used for cache records."""
    return os.getenv("CACHE_TABLE", "jay-asset-cache")


def cache_ttl_seconds() -> int:
    """Return cache TTL in seconds, with a safe default on invalid input."""
    try:
        return int(os.getenv("CACHE_TTL_SECONDS", "7200"))  # 2 hours
    except ValueError:
        return 7200

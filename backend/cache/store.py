import json
import time

from .config import cache_enabled, cache_table_name, cache_ttl_seconds

try:
    import boto3  # Available by default in AWS Lambda Python runtimes
except Exception:  # pragma: no cover - best effort for local envs without boto3
    boto3 = None


def _ddb_table():
    """Return the configured DynamoDB table handle, or None when unavailable."""
    if boto3 is None:
        return None
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(cache_table_name())


def cache_get_plan(cache_key: str):
    """Read a cached plan by key and return None for misses, expiry, or parse errors."""
    if not cache_enabled():
        return None

    table = _ddb_table()
    if table is None:
        return None

    try:
        response = table.get_item(Key={"cache_key": cache_key})
    except Exception:
        return None

    item = response.get("Item")
    if not item:
        return None

    expires_at = item.get("expires_at")
    try:
        if expires_at is not None and int(expires_at) <= int(time.time()):
            return None
    except Exception:
        pass

    value = item.get("value")
    if not isinstance(value, str) or not value:
        return None

    try:
        plan = json.loads(value)
    except Exception:
        return None

    return plan if isinstance(plan, dict) else None


def cache_set_plan(cache_key: str, plan: dict):
    """Persist a plan in cache with TTL; failures are intentionally ignored."""
    if not cache_enabled():
        return

    table = _ddb_table()
    if table is None:
        return

    try:
        table.put_item(
            Item={
                "cache_key": cache_key,
                "expires_at": int(time.time()) + cache_ttl_seconds(),
                "value": json.dumps(plan, separators=(",", ":"), ensure_ascii=False),
            }
        )
    except Exception:
        # Best-effort cache
        return

import json
import time

from .config import performance_enabled, performance_table_name, performance_ttl_seconds

try:
    import boto3  # Available by default in AWS Lambda Python runtimes
except Exception:  # pragma: no cover
    boto3 = None


def _ddb_table():
    if boto3 is None:
        return None
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(performance_table_name())


def _metric_key(strategy_id: str, bucket: str = "default") -> str:
    return f"{strategy_id}|{bucket}"


def performance_get_metrics(strategy_id: str, bucket: str = "default"):
    if not performance_enabled():
        return None
    table = _ddb_table()
    if table is None:
        return None
    try:
        response = table.get_item(Key={"metric_key": _metric_key(strategy_id, bucket)})
    except Exception:
        return None
    item = response.get("Item")
    if not item:
        return None

    value = item.get("value")
    if not isinstance(value, str) or not value:
        return None
    try:
        metrics = json.loads(value)
    except Exception:
        return None
    return metrics if isinstance(metrics, dict) else None


def performance_set_metrics(strategy_id: str, metrics: dict, bucket: str = "default"):
    if not performance_enabled():
        return False
    table = _ddb_table()
    if table is None:
        return False
    try:
        table.put_item(
            Item={
                "metric_key": _metric_key(strategy_id, bucket),
                "expires_at": int(time.time()) + performance_ttl_seconds(),
                "updated_at": int(time.time()),
                "value": json.dumps(metrics, separators=(",", ":"), ensure_ascii=False),
            }
        )
        return True
    except Exception:
        return False

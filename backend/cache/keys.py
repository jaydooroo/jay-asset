import json
from datetime import datetime, timezone


def _today_bucket_utc() -> str:
    """Return today's UTC date bucket so cache keys rotate daily."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _normalize_tickers(value):
    """Normalize tickers to uppercase, deduplicated, and sorted list form."""
    if isinstance(value, str):
        parts = [part.strip().upper() for part in value.split(",")]
    elif isinstance(value, list):
        parts = [str(part).strip().upper() for part in value]
    else:
        return value

    parts = [part for part in parts if part]
    return sorted(dict.fromkeys(parts))


def _canonical_parameters(strategy_id: str, parameters: dict) -> dict:
    """Normalize strategy parameters so equivalent requests share one cache key."""
    if not isinstance(parameters, dict):
        return {}

    normalized = dict(parameters)
    if strategy_id == "paa" and "etfs" in normalized:
        normalized["etfs"] = _normalize_tickers(normalized["etfs"])
        for key in ("top_n", "lookback_months"):
            if isinstance(normalized.get(key), str):
                try:
                    normalized[key] = int(normalized[key].strip())
                except Exception:
                    pass

    if strategy_id == "vaa":
        if "offensive_assets" in normalized:
            normalized["offensive_assets"] = _normalize_tickers(normalized["offensive_assets"])
        if "defensive_assets" in normalized:
            normalized["defensive_assets"] = _normalize_tickers(normalized["defensive_assets"])

    return normalized


def cache_key(strategy_id: str, parameters: dict) -> str | None:
    """Build a stable key from date bucket, strategy id, and canonical parameters."""
    try:
        params_json = json.dumps(
            _canonical_parameters(strategy_id, parameters),
            sort_keys=True,
            separators=(",", ":"),
        )
    except Exception:
        return None

    return f"{_today_bucket_utc()}|{strategy_id}|{params_json}"

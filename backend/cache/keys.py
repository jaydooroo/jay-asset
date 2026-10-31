import hashlib
import inspect
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from strategies.static_allocation import STATIC_PORTFOLIOS, parse_weights


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

    if strategy_id == "cdm":
        for key in ("equity_assets", "credit_assets", "reit_assets", "hedge_assets"):
            if key in normalized:
                normalized[key] = _normalize_tickers(normalized[key])
        if "cash_asset" in normalized:
            normalized["cash_asset"] = str(normalized["cash_asset"]).strip().upper()
        if isinstance(normalized.get("lookback_months"), str):
            try:
                normalized["lookback_months"] = int(normalized["lookback_months"].strip())
            except Exception:
                pass

    if strategy_id == "daa":
        for key in ("offensive_assets", "defensive_assets", "canary_assets"):
            if key in normalized:
                normalized[key] = _normalize_tickers(normalized[key])
        if isinstance(normalized.get("top_n"), str):
            try:
                normalized["top_n"] = int(normalized["top_n"].strip())
            except Exception:
                pass

    if strategy_id in STATIC_PORTFOLIOS and "weights" in normalized:
        # "SPY:60,AGG:40" and {"AGG": 4, "SPY": 6} are the same portfolio.
        normalized["weights"] = parse_weights(normalized["weights"]) or normalized["weights"]

    if strategy_id == "gtaa" and "risk_assets" in normalized:
        normalized["risk_assets"] = _normalize_tickers(normalized["risk_assets"])

    for key in ("lookback_months", "sma_months"):
        if strategy_id in ("gem", "gtaa") and key in normalized:
            try:
                normalized[key] = int(float(str(normalized[key]).strip()))
            except Exception:
                pass

    return normalized


@lru_cache(maxsize=None)
def _code_version(strategy_cls: type) -> str:
    """
    Short hash of the strategy's source files (its class and base classes).

    Deploying changed strategy code changes the hash, so plans cached by the
    previous code are no longer read.
    """
    digest = hashlib.sha256()
    files = {inspect.getsourcefile(cls) for cls in strategy_cls.__mro__ if cls is not object}
    for path in sorted(f for f in files if f):
        digest.update(Path(path).read_bytes())
    return digest.hexdigest()[:8]


def cache_key(strategy_id: str, parameters: dict, strategy=None) -> str | None:
    """Build a stable key from date bucket, strategy id + code version, and canonical parameters."""
    try:
        params_json = json.dumps(
            _canonical_parameters(strategy_id, parameters),
            sort_keys=True,
            separators=(",", ":"),
        )
        version = f"@{_code_version(type(strategy))}" if strategy is not None else ""
    except Exception:
        return None

    return f"{_today_bucket_utc()}|{strategy_id}{version}|{params_json}"

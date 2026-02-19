def _normalize_ticker_list(value):
    if isinstance(value, str):
        parts = [part.strip().upper() for part in value.split(",")]
    elif isinstance(value, list):
        parts = [str(part).strip().upper() for part in value]
    else:
        return value
    return [part for part in parts if part]


def strategy_default_parameters(strategy) -> dict:
    """
    Legacy helper for building defaults from strategy UI metadata.

    The scheduled performance pipeline now gets defaults from
    explicit performance specs (`performance/specs/*`), but this
    helper remains available for compatibility.

    Build strategy defaults from `get_parameters()` metadata.
    """
    out = {}
    for param in strategy.get_parameters() or []:
        name = param.get("name")
        if not name or "default" not in param:
            continue
        raw = param.get("default")
        ptype = param.get("type")

        if ptype == "number":
            try:
                number = float(raw)
                out[name] = int(number) if number.is_integer() else number
            except Exception:
                continue
            continue

        if name == "etfs" or name.endswith("_assets"):
            out[name] = _normalize_ticker_list(raw)
            continue

        out[name] = raw
    return out

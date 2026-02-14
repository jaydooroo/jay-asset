def scale_plan(plan: dict, total_money: float, strategy_name: str) -> dict:
    """Convert weight-only plan output into concrete money allocation amounts."""
    weights = plan.get("allocation_weights")
    if not isinstance(weights, dict) or not weights:
        return {"error": "Cached plan missing allocation_weights"}

    allocation = {}
    for ticker, weight in weights.items():
        try:
            current_weight = float(weight)
        except Exception:
            continue
        if current_weight <= 0:
            continue
        allocation[str(ticker)] = round(float(total_money) * current_weight, 2)

    if allocation:
        diff = round(float(total_money) - sum(allocation.values()), 2)
        if abs(diff) >= 0.01:
            try:
                best = max(allocation.keys(), key=lambda key: float(weights.get(key, 0.0)))
                allocation[best] = round(allocation[best] + diff, 2)
            except Exception:
                pass

    result = dict(plan)
    result["strategy"] = strategy_name
    result["total_amount"] = float(total_money)
    result["allocation_weights"] = weights
    result["allocation"] = allocation
    return result

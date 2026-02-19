from .backtest import run_monthly_walkforward_backtest
from .specs import get_performance_spec, list_performance_spec_ids
from .store import performance_set_metrics


def compute_and_store_for_strategy(strategy_id: str) -> dict:
    spec = get_performance_spec(strategy_id)
    if not spec:
        return {
            "strategy_id": strategy_id,
            "ok": False,
            "error": f"No performance spec registered for strategy '{strategy_id}'",
        }

    result = run_monthly_walkforward_backtest(spec, spec.default_parameters())
    if not isinstance(result, dict):
        return {"strategy_id": strategy_id, "ok": False, "error": "Backtest returned invalid result"}
    if "error" in result:
        return {
            "strategy_id": strategy_id,
            "ok": False,
            "error": result.get("error", "Backtest failed"),
        }

    payload = {
        "strategy_id": strategy_id,
        "strategy_name": spec.strategy_name,
        "strategy_version": spec.strategy_version,
        "rebalance_frequency": spec.rebalance_frequency,
        "parameters": result.get("parameters", {}),
        "metrics": result.get("metrics", {}),
    }
    saved = performance_set_metrics(strategy_id, payload)
    if not saved:
        return {
            "strategy_id": strategy_id,
            "ok": False,
            "error": "Failed to persist performance metrics (check DynamoDB table/IAM/env)",
        }
    return {"strategy_id": strategy_id, "ok": True, "metrics": payload.get("metrics", {})}


def run_monthly_performance_refresh() -> dict:
    results = []
    for strategy_id in list_performance_spec_ids():
        results.append(compute_and_store_for_strategy(strategy_id))

    ok_count = sum(1 for r in results if r.get("ok"))
    return {
        "ok": ok_count == len(results),
        "total": len(results),
        "updated": ok_count,
        "results": results,
    }


def run_daily_performance_refresh() -> dict:
    """
    Backward-compatible alias used by existing Lambda schedule wiring.
    Internally this now runs the monthly walk-forward refresh logic.
    """
    return run_monthly_performance_refresh()

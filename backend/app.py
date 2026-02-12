from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import json
import os
import time
from strategies import get_strategy, list_strategies

# DynamoDB cache (optional)
try:
    import boto3  # Available by default in AWS Lambda Python runtimes
except Exception:  # pragma: no cover - best effort for local envs without boto3
    boto3 = None

# Flask backend API for the React frontend.
# Provides:
# - GET  /api/strategies : list available strategies + UI parameters
# - POST /api/calculate  : run a strategy calculation
# - GET  /api/history    : returns empty (no persistence for Lambda deployment)
# - GET  /api/health     : simple health check
app = Flask(__name__)

# CORS
# - In local dev, React runs on http://localhost:3000 and calls this API on :5000.
# - In AWS Lambda behind a Function URL/API Gateway, configure CORS there instead.
#   Enabling both can produce duplicate `Access-Control-Allow-Origin` values
#   (e.g. "http://localhost:3000, *") which browsers reject.
if not os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    allowed = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    allowed = [o.strip() for o in allowed if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": allowed}})


def _cache_enabled() -> bool:
    # Enable by default in Lambda; allow disabling explicitly.
    if os.getenv("CACHE_ENABLED", "").strip().lower() in {"0", "false", "no"}:
        return False
    return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def _cache_table_name() -> str:
    return os.getenv("CACHE_TABLE", "jay-asset-cache")


def _cache_ttl_seconds() -> int:
    try:
        return int(os.getenv("CACHE_TTL_SECONDS", "21600"))  # 6 hours
    except ValueError:
        return 21600


def _today_bucket_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _normalize_tickers(value):
    if isinstance(value, str):
        parts = [p.strip().upper() for p in value.split(",")]
    elif isinstance(value, list):
        parts = [str(p).strip().upper() for p in value]
    else:
        return value

    parts = [p for p in parts if p]
    # For caching purposes, order shouldn't matter.
    return sorted(dict.fromkeys(parts))


def _canonical_parameters(strategy_id: str, parameters: dict) -> dict:
    if not isinstance(parameters, dict):
        return {}

    out = dict(parameters)
    if strategy_id == "paa" and "etfs" in out:
        out["etfs"] = _normalize_tickers(out["etfs"])
    if strategy_id == "vaa":
        if "offensive_assets" in out:
            out["offensive_assets"] = _normalize_tickers(out["offensive_assets"])
        if "defensive_assets" in out:
            out["defensive_assets"] = _normalize_tickers(out["defensive_assets"])
    return out


def _cache_key(strategy_id: str, parameters: dict) -> str:
    params_json = json.dumps(_canonical_parameters(strategy_id, parameters), sort_keys=True, separators=(",", ":"))
    return f"{_today_bucket_utc()}|{strategy_id}|{params_json}"


def _ddb_table():
    if boto3 is None:
        return None
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(_cache_table_name())


def _cache_get_plan(cache_key: str):
    if not _cache_enabled():
        return None

    table = _ddb_table()
    if table is None:
        return None

    try:
        resp = table.get_item(Key={"cache_key": cache_key})
    except Exception:
        return None

    item = resp.get("Item")
    if not item:
        return None

    value = item.get("value")
    if not isinstance(value, str) or not value:
        return None

    try:
        plan = json.loads(value)
    except Exception:
        return None

    return plan if isinstance(plan, dict) else None


def _cache_set_plan(cache_key: str, plan: dict):
    if not _cache_enabled():
        return

    table = _ddb_table()
    if table is None:
        return

    try:
        table.put_item(
            Item={
                "cache_key": cache_key,
                "expires_at": int(time.time()) + _cache_ttl_seconds(),
                "value": json.dumps(plan, separators=(",", ":"), ensure_ascii=False),
            }
        )
    except Exception:
        # Best-effort cache
        return


def _scale_plan(plan: dict, total_money: float, strategy_name: str) -> dict:
    weights = plan.get("allocation_weights")
    if not isinstance(weights, dict) or not weights:
        return {"error": "Cached plan missing allocation_weights"}

    allocation = {}
    for ticker, weight in weights.items():
        try:
            w = float(weight)
        except Exception:
            continue
        if w <= 0:
            continue
        allocation[str(ticker)] = round(float(total_money) * w, 2)

    # Fix rounding so totals match total_money.
    if allocation:
        diff = round(float(total_money) - sum(allocation.values()), 2)
        if abs(diff) >= 0.01:
            try:
                best = max(allocation.keys(), key=lambda k: float(weights.get(k, 0.0)))
                allocation[best] = round(allocation[best] + diff, 2)
            except Exception:
                pass

    result = dict(plan)
    result["strategy"] = strategy_name
    result["total_amount"] = float(total_money)
    result["allocation_weights"] = weights
    result["allocation"] = allocation
    return result

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get list of all available strategies"""
    try:
        strategies = list_strategies()
        return jsonify({
            'success': True,
            'strategies': strategies
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate', methods=['POST'])
def calculate_allocation():
    """Calculate allocation for a given strategy"""
    try:
        # Request body is JSON (see src/services/api.js)
        data = request.json
        strategy_id = data.get('strategy_id')
        total_money = float(data.get('total_money', 0))
        parameters = data.get('parameters', {})


        if not strategy_id:
            return jsonify({
                'success': False,
                'error': 'Strategy ID is required'
            }), 400

        if total_money <= 0:
            return jsonify({
                'success': False,
                'error': 'Total money must be greater than 0'
            }), 400

        # Get strategy and calculate.
        # Note: strategies implement calculate_allocation(total_money, **parameters).
        strategy = get_strategy(strategy_id)
        if not strategy:
            return jsonify({
                'success': False,
                'error': f'Strategy {strategy_id} not found'
            }), 404

        ck = _cache_key(strategy_id, parameters)
        cached_plan = _cache_get_plan(ck)
        if cached_plan:
            result = _scale_plan(cached_plan, total_money, strategy.name)
            if "error" not in result:
                return jsonify({
                    'success': True,
                    'result': result,
                    'cached': True,
                })

        plan = strategy.calculate_plan(**parameters)
        if not isinstance(plan, dict):
            return jsonify({
                'success': False,
                'error': 'Strategy returned invalid plan'
            }), 500

        if 'error' in plan:
            return jsonify({
                'success': False,
                'error': plan['error']
            }), 500

        _cache_set_plan(ck, plan)
        result = _scale_plan(plan, total_money, strategy.name)

        # Check for errors in result
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500

        return jsonify({
            'success': True,
            'result': result,
            'cached': False,
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get calculation history - returns empty (stateless for Lambda)"""
    return jsonify({
        'success': True,
        'history': []
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

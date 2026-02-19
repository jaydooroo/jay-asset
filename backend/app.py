from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from strategies import get_strategy, list_strategies
from cache import cache_key, cache_get_plan, cache_set_plan, scale_plan
from performance import compute_and_store_for_strategy, performance_get_metrics

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

        ck = cache_key(strategy_id, parameters)
        if ck:
            cached_plan = cache_get_plan(ck)
            if cached_plan:
                result = scale_plan(cached_plan, total_money, strategy.name)
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

        if ck:
            cache_set_plan(ck, plan)
        result = scale_plan(plan, total_money, strategy.name)

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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/performance', methods=['GET'])
def get_performance():
    """
    Return cached monthly walk-forward performance metrics for a strategy.

    Query params:
      - strategy_id (required): e.g. 'paa'
      - refresh (optional): '1'/'true' to force recompute now
    """
    strategy_id = (request.args.get('strategy_id') or '').strip()
    if not strategy_id:
        return jsonify({
            'success': False,
            'error': 'strategy_id is required'
        }), 400

    if not get_strategy(strategy_id):
        return jsonify({
            'success': False,
            'error': f'Strategy {strategy_id} not found'
        }), 404

    refresh = (request.args.get('refresh') or '').strip().lower() in {'1', 'true', 'yes'}
    if refresh:
        result = compute_and_store_for_strategy(strategy_id)
        if not result.get('ok'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to compute performance metrics')
            }), 500

    payload = performance_get_metrics(strategy_id)
    if not payload:
        # Best-effort warmup for first run / empty table
        result = compute_and_store_for_strategy(strategy_id)
        if not result.get('ok'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'No cached performance metrics available')
            }), 404
        payload = performance_get_metrics(strategy_id)
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Performance metrics were computed but could not be persisted. Check DynamoDB table, IAM, and PERFORMANCE_* env vars.'
            }), 503

    return jsonify({
        'success': True,
        'performance': payload
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

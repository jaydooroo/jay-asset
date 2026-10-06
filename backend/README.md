# Backend Setup

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements-dev.txt
```

## Running the Backend

```bash
python app.py
```

The backend will run on `http://localhost:5000`

## Deployment

The backend is deployed with AWS SAM (`template.yaml` at the project root):

```powershell
.\scripts\deploy-backend.ps1
```

Lambda settings, environment variables, and schedules are defined in `template.yaml`.
See [docs/deployment.md](../docs/deployment.md) for setup and the full procedure.

## API Endpoints

### GET `/api/strategies`
Get list of all available strategies

### POST `/api/calculate`
Calculate asset allocation

**Request Body:**
```json
{
  "strategy_id": "paa",
  "total_money": 10000,
  "parameters": {
    "etfs": ["SPY", "QQQ", "IWM"],
    "top_n": 6,
    "lookback_months": 12
  }
}
```

### GET `/api/history`
Get calculation history

### GET `/api/health`
Health check endpoint

### GET `/api/performance?strategy_id=paa`
Get monthly walk-forward performance metrics (precomputed/cached).

- Query params:
  - `strategy_id` (required)
  - `refresh` (optional: `true|1`) to force immediate recompute

## Optional DynamoDB Cache (Lambda)

The `/api/calculate` endpoint can cache strategy plans (allocation weights) in DynamoDB to avoid repeated
market-data downloads for identical inputs.

Environment variables:
- `CACHE_ENABLED`: `true|false` (defaults to enabled in Lambda, disabled elsewhere)
- `CACHE_TABLE`: DynamoDB table name (default: `jay-asset-cache`)
- `CACHE_TTL_SECONDS`: TTL in seconds (default: `7200` = 2 hours)

Table requirements:
- Partition key: `cache_key` (String)
- TTL attribute (optional but recommended): `expires_at` (Number)

## Monthly Strategy Performance Snapshot (Lambda + EventBridge)

The backend supports scheduled precomputation of basic metrics so users can view expected
performance without heavy per-request backtesting.

Metrics produced (walk-forward monthly backtest):
- cumulative return
- CAGR
- max drawdown
- annualized volatility

Environment variables:
- `PERFORMANCE_ENABLED`: `true|false` (defaults to enabled in Lambda, disabled elsewhere)
- `PERFORMANCE_TABLE`: DynamoDB table name (default: `jay-asset-performance`)
- `PERFORMANCE_LOOKBACK_DAYS`: minimum trading-day lookback per rebalance step (default: `252` for ~1Y)
- `PERFORMANCE_BACKTEST_MONTHS`: monthly periods to simulate (default: `12`)
- `PERFORMANCE_TTL_SECONDS`: item TTL (default: `5184000` = 60 days)

Table requirements:
- Partition key: `metric_key` (String)
- TTL attribute (optional but recommended): `expires_at` (Number)

Lambda schedule:
- `backend/lambda_handler.py` handles EventBridge schedule events (`aws.events` / `aws.scheduler`)
- Scheduled invocation runs monthly refresh for all registered strategy specs.

Adding strategies:
- Add a new strategy spec under `backend/performance/specs/`
- Register it in `backend/performance/specs/__init__.py`
- The shared engine in `backend/performance/backtest.py` handles monthly walk-forward simulation.

## Adding New Strategies

Before implementation, read:
- `backend/NEW_STRATEGY_CHECKLIST.md` (covers runtime logic, cache normalization, performance spec, i18n, and verification)

1. Create a new file in `strategies/` (e.g., `my_strategy.py`)
2. Inherit from `BaseStrategy`
3. Implement `calculate_allocation()` and `get_parameters()`
4. Register in `strategies/__init__.py`

Example:
```python
from .base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="My Strategy",
            description="Description here"
        )

    def calculate_allocation(self, total_money, **kwargs):
        # Your calculation logic
        return {
            'allocation': {'SPY': 5000, 'BND': 5000},
            'strategy': self.name,
            'total_amount': total_money
        }

    def get_parameters(self):
        return []
```

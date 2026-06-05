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
pip install -r requirements.txt
```

## Running the Backend

```bash
python app.py
```

The backend will run on `http://localhost:5000`

## Building the AWS Lambda Deployment Package

The backend is deployed to AWS Lambda as a zip file:

```text
backend/deployment.zip
```

Build this zip with Docker instead of installing dependencies directly on Windows. AWS Lambda
runs on Linux, and compiled packages such as `numpy` and `pandas` need Linux-compatible files.

### 1. Go to the project root

Run this from PowerShell:

```powershell
cd D:\project\JehyeonAssetManagement\jay-asset
```

The project root is the folder that contains:

```text
backend/
src/
public/
package.json
docker-compose.yml
```

### 2. Confirm Docker is running

```powershell
docker ps
```

If this fails, open Docker Desktop first and wait until the Docker engine is running.

### 3. Build `backend/deployment.zip`

```powershell
docker run --rm `
  -v "${PWD}/backend:/var/task" `
  public.ecr.aws/sam/build-python3.11:latest `
  /bin/sh -c "rm -rf /var/task/lambda_build /var/task/deployment.zip && mkdir -p /var/task/lambda_build && pip install -r /var/task/requirements.txt -t /var/task/lambda_build && cp /var/task/*.py /var/task/lambda_build/ && cp -r /var/task/strategies /var/task/cache /var/task/market /var/task/performance /var/task/lambda_build/ && cd /var/task/lambda_build && zip -r /var/task/deployment.zip ."
```

This command:

1. Starts a temporary AWS SAM Python 3.11 build container.
2. Mounts the local `backend/` folder as `/var/task` inside the container.
3. Removes any old `lambda_build/` folder and old `deployment.zip`.
4. Installs `requirements.txt` into `lambda_build/`.
5. Copies backend source files and folders into `lambda_build/`.
6. Creates `backend/deployment.zip`.

### 4. Confirm the zip exists

```powershell
Get-Item .\backend\deployment.zip
```

The file should have a non-zero size, usually tens of MB because it includes dependencies.

### Lambda settings

When uploading this zip to AWS Lambda, use:

```text
Runtime: Python 3.11
Handler: lambda_handler.handler
```

Recommended environment variables:

```text
MARKET_PRICE_SOURCE=dynamodb
MARKET_PRICE_TABLE=jay-asset-daily-prices

PERFORMANCE_ENABLED=true
PERFORMANCE_TABLE=jay-asset-performance

CACHE_ENABLED=true
CACHE_TABLE=jay-asset-cache

MARKET_INGEST_PROVIDER=tiingo
TIINGO_API_KEY=<your-tiingo-api-key>

AWS_DEFAULT_REGION=us-east-1
```

Do not set `MARKET_DYNAMODB_ENDPOINT_URL` in AWS Lambda. That variable is only for local
DynamoDB running in Docker.

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

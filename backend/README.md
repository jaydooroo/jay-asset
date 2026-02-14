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

## Adding New Strategies

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

# DynamoDB Local setup

This project can use the same market-data repository code against either AWS
DynamoDB or DynamoDB Local.

## 1. Start DynamoDB Local

```powershell
docker compose up -d dynamodb-local
```

DynamoDB Local listens on:

```text
http://localhost:8000
```

The local container persists data under:

```text
.dynamodb-local/
```

That folder is ignored by git. If you delete it, recreate the table and ingest
data again.

## Optional: start a browser UI

This project includes `dynamodb-admin`, a small browser UI for DynamoDB Local.

```powershell
docker compose up -d dynamodb-admin
```

Open:

```text
http://localhost:8001
```

The UI connects to DynamoDB Local through Docker's internal network:

```text
dynamodb-admin -> http://dynamodb-local:8000
```

## 2. Install backend dependencies

```powershell
cd backend
pip install -r requirements-dev.txt
```

If you are using the project virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## 3. Create the local price table

```powershell
$env:MARKET_DYNAMODB_ENDPOINT_URL="http://localhost:8000"
$env:MARKET_PRICE_TABLE="jay-asset-daily-prices"
$env:AWS_DEFAULT_REGION="us-east-1"

.\.venv\Scripts\python.exe scripts/create_market_price_table.py
```

## 4. Ingest prices from Tiingo

Prices always come from Tiingo. Set your API token and ingest the default
strategy tickers:

```powershell
$env:TIINGO_API_KEY="your_token_here"

.\.venv\Scripts\python.exe scripts/ingest_market_prices.py --tickers AGG,BIL,BND,DBC,EEM,EFA,EWJ,EWM,EWY,GLD,HYG,IEF,IWD,IWM,LQD,QQQ,REM,SHY,SPY,TLT,VBR,VGK,VNQ,VWO --lookback-days 900
```

Rows written through this path use `source = tiingo`.

Without a Tiingo token, seed deterministic fake prices instead so you can still
test the application flow:

```powershell
.\.venv\Scripts\python.exe scripts/seed_sample_market_prices.py --trading-days 756
```

Seeded rows use `source = sample` and are not real market prices.

## Inspect stored market prices

After seeding or ingesting, inspect ticker coverage:

```powershell
.\.venv\Scripts\python.exe scripts/inspect_market_prices.py
```

Inspect a subset:

```powershell
.\.venv\Scripts\python.exe scripts/inspect_market_prices.py --tickers SPY,QQQ,IEF
```

Show latest raw items too:

```powershell
.\.venv\Scripts\python.exe scripts/inspect_market_prices.py --tickers SPY --sample-limit 3
```

## 5. Run the backend against DynamoDB Local

The backend always reads prices from DynamoDB; the endpoint decides which one.

```powershell
$env:MARKET_DYNAMODB_ENDPOINT_URL="http://localhost:8000"
$env:MARKET_PRICE_TABLE="jay-asset-daily-prices"
$env:AWS_DEFAULT_REGION="us-east-1"

.\.venv\Scripts\python.exe app.py
```

To read the real AWS table instead (no Docker needed), load your AWS settings
with `.\scripts\load-backend-env.ps1` from the project root and leave
`MARKET_DYNAMODB_ENDPOINT_URL` unset.

## AWS deployment difference

In AWS, do **not** set `MARKET_DYNAMODB_ENDPOINT_URL`. Set
`MARKET_PRICE_TABLE=jay-asset-daily-prices` and grant the Lambda role
permission to read/write that DynamoDB table (see `template.yaml`).

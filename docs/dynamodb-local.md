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
pip install -r requirements.txt
```

If you are using the project virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Create the local price table

```powershell
$env:MARKET_DYNAMODB_ENDPOINT_URL="http://localhost:8000"
$env:MARKET_PRICE_TABLE="jay-asset-daily-prices"
$env:AWS_DEFAULT_REGION="us-east-1"

.\.venv\Scripts\python.exe scripts/create_market_price_table.py
```

## 4. Ingest sample data

Preferred when the external providers are working:

```powershell
$env:MARKET_INGEST_TICKERS="SPY,QQQ,IWM,VGK,EWJ,EEM,VNQ,GLD,DBC,HYG,LQD,IEF"

.\.venv\Scripts\python.exe scripts/ingest_market_prices.py --lookback-days 900
```

The ingest script still calls the external market providers. Local DynamoDB only
replaces the storage layer.

If Stooq/Yahoo are unavailable, seed deterministic fake prices instead so you
can still test the DynamoDB-backed application flow:

```powershell
.\.venv\Scripts\python.exe scripts/seed_sample_market_prices.py --trading-days 756
```

Seeded rows use `source = sample` and are not real market prices.

## Tiingo ingest

If Yahoo/Stooq are unavailable, use Tiingo with an API token:

```powershell
$env:MARKET_INGEST_PROVIDER="tiingo"
$env:TIINGO_API_KEY="your_token_here"

.\.venv\Scripts\python.exe scripts/ingest_market_prices.py --tickers SPY --lookback-days 30
```

For all default strategy tickers:

```powershell
.\.venv\Scripts\python.exe scripts/ingest_market_prices.py --tickers SPY,QQQ,IWM,VGK,EWJ,EEM,VNQ,GLD,DBC,HYG,LQD,IEF,EFA,AGG,SHY,REM,TLT,BIL --lookback-days 900
```

Rows written through this path use `source = tiingo`.

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

## 5. Run the backend using DynamoDB as price source

```powershell
$env:MARKET_PRICE_SOURCE="dynamodb"
$env:MARKET_DYNAMODB_ENDPOINT_URL="http://localhost:8000"
$env:MARKET_PRICE_TABLE="jay-asset-daily-prices"
$env:AWS_DEFAULT_REGION="us-east-1"

.\.venv\Scripts\python.exe app.py
```

Now `/api/calculate` reads historical prices from DynamoDB Local instead of
calling Yahoo/Stooq during the user request.

## AWS deployment difference

In AWS, do **not** set `MARKET_DYNAMODB_ENDPOINT_URL`.

Use:

```text
MARKET_PRICE_SOURCE=dynamodb
MARKET_PRICE_TABLE=jay-asset-daily-prices
```

and grant the Lambda role permission to read/write that DynamoDB table.

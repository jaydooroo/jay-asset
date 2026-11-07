"""
Price storage: reading from DynamoDB, downloading from Tiingo and the daily
ingest job. boto3 and requests are replaced by small fakes, so nothing here
touches AWS or the network.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pandas as pd
import pytest
import requests

from market import dynamodb_repository, ingest
from market.dynamodb_repository import DynamoDBPriceRepository
from market.providers import tiingo
from market.providers.tiingo import TiingoPriceRepository


# --- DynamoDB reads ---------------------------------------------------------

class FakePriceTable:
    """Answers `query` like DynamoDB: one ticker's rows, `page_size` at a time."""

    def __init__(self, rows, page_size=2):
        self.rows = rows  # {ticker: [(date, close), ...]}
        self.page_size = page_size
        self.queries = []

    def query(self, KeyConditionExpression, ExclusiveStartKey=None):
        ticker_cond, date_cond = KeyConditionExpression.get_expression()["values"]
        ticker = ticker_cond.get_expression()["values"][1]
        _, start, end = date_cond.get_expression()["values"]
        self.queries.append((ticker, start, end))

        items = [{"ticker": ticker, "price_date": d, "close": c}
                 for d, c in self.rows.get(ticker, []) if start <= d <= end]
        offset = ExclusiveStartKey["offset"] if ExclusiveStartKey else 0
        page = items[offset:offset + self.page_size]
        response = {"Items": page}
        if offset + self.page_size < len(items):
            response["LastEvaluatedKey"] = {"offset": offset + self.page_size}
        return response


@pytest.fixture
def ddb_table(monkeypatch):
    def install(rows, page_size=2):
        table = FakePriceTable(rows, page_size)
        resource = type("Resource", (), {"Table": lambda self, name: table})()
        monkeypatch.setattr(dynamodb_repository, "dynamodb_resource", lambda: resource)
        return table

    return install


class TestDynamoDBPriceRepository:
    def test_reads_every_page_and_builds_a_sorted_frame(self, ddb_table):
        ddb_table({
            "SPY": [("2026-10-01", Decimal("100.5")), ("2026-10-02", Decimal("101")),
                    ("2026-10-05", Decimal("99.25")), ("2026-10-06", Decimal("100"))],
            "AGG": [("2026-10-02", Decimal("98"))],
        })
        prices, failed = DynamoDBPriceRepository("t").get_close_prices(
            ["spy", " AGG "], datetime(2026, 10, 1), datetime(2026, 10, 31))

        assert failed == []
        assert list(prices.columns) == ["SPY", "AGG"]
        assert prices["SPY"].tolist() == [100.5, 101.0, 99.25, 100.0]
        assert prices.loc["2026-10-02", "AGG"] == 98.0
        assert pd.isna(prices.loc["2026-10-01", "AGG"])

    def test_queries_the_requested_date_range(self, ddb_table):
        table = ddb_table({"SPY": [("2026-09-30", 1), ("2026-10-01", 2), ("2026-10-31", 3), ("2026-11-02", 4)]})
        prices, _ = DynamoDBPriceRepository("t").get_close_prices(["SPY"], datetime(2026, 10, 1), datetime(2026, 10, 31))
        assert table.queries[0] == ("SPY", "2026-10-01", "2026-10-31")
        assert prices["SPY"].tolist() == [2.0, 3.0]

    def test_tickers_without_rows_are_reported(self, ddb_table):
        ddb_table({"SPY": [("2026-10-01", 1)]})
        prices, failed = DynamoDBPriceRepository("t").get_close_prices(
            ["SPY", "IWD"], datetime(2026, 10, 1), datetime(2026, 10, 2))
        assert failed == ["IWD"]
        assert list(prices.columns) == ["SPY"]

    def test_nothing_found_gives_an_empty_frame(self, ddb_table):
        ddb_table({})
        prices, failed = DynamoDBPriceRepository("t").get_close_prices(["VBR"], datetime(2026, 1, 1), datetime(2026, 2, 1))
        assert prices.empty
        assert failed == ["VBR"]


# --- Tiingo -----------------------------------------------------------------

class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload, self.status = payload, status

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(f"{self.status}")

    def json(self):
        return self.payload


class FakeSession:
    responses = {}

    def __init__(self):
        self.headers = {}
        self.requests = []

    def get(self, url, params=None, timeout=None):
        ticker = url.rstrip("/").split("/")[-2]
        self.requests.append((ticker, params))
        FakeSession.last = self
        return self.responses[ticker]


@pytest.fixture
def tiingo_responses(monkeypatch):
    monkeypatch.setattr(tiingo.requests, "Session", FakeSession)

    def install(responses):
        FakeSession.responses = responses

    return install


class TestTiingo:
    def test_uses_dividend_adjusted_close(self, tiingo_responses):
        tiingo_responses({"AGG": FakeResponse([
            {"date": "2026-10-01T00:00:00.000Z", "close": 98.0, "adjClose": 97.1},
            {"date": "2026-10-02T00:00:00.000Z", "close": 98.5, "adjClose": 97.6},
        ])})
        prices, failed = TiingoPriceRepository("key").get_close_prices(["agg"], datetime(2026, 10, 1), datetime(2026, 10, 2))
        assert failed == []
        assert prices["AGG"].tolist() == [97.1, 97.6]
        assert list(prices.index) == [pd.Timestamp("2026-10-01"), pd.Timestamp("2026-10-02")]

    def test_sends_token_and_date_range(self, tiingo_responses):
        tiingo_responses({"SPY": FakeResponse([{"date": "2026-10-01", "close": 1}])})
        TiingoPriceRepository("secret").get_close_prices(["SPY"], datetime(2026, 9, 1), datetime(2026, 10, 1))
        session = FakeSession.last
        assert session.headers["Authorization"] == "Token secret"
        assert session.requests == [("SPY", {"startDate": "2026-09-01", "endDate": "2026-10-01", "format": "json"})]

    def test_falls_back_to_close_without_adjusted_close(self, tiingo_responses):
        tiingo_responses({"SPY": FakeResponse([{"date": "2026-10-01", "close": 500.0}])})
        prices, _ = TiingoPriceRepository("key").get_close_prices(["SPY"], datetime(2026, 10, 1), datetime(2026, 10, 1))
        assert prices["SPY"].tolist() == [500.0]

    @pytest.mark.parametrize("response", [FakeResponse([], 200), FakeResponse({"detail": "x"}, 404),
                                          FakeResponse([{"date": "2026-10-01"}])])
    def test_unusable_responses_mark_the_ticker_failed(self, tiingo_responses, response):
        tiingo_responses({"BAD": response, "SPY": FakeResponse([{"date": "2026-10-01", "close": 1}])})
        prices, failed = TiingoPriceRepository("key").get_close_prices(["BAD", "SPY"], datetime(2026, 10, 1), datetime(2026, 10, 1))
        assert failed == ["BAD"]
        assert list(prices.columns) == ["SPY"]

    def test_requires_an_api_key(self, monkeypatch):
        monkeypatch.delenv("TIINGO_API_KEY", raising=False)
        with pytest.raises(RuntimeError):
            TiingoPriceRepository()


# --- Ingest job -------------------------------------------------------------

class FakeBatchTable:
    def __init__(self):
        self.items = []

    def batch_writer(self, overwrite_by_pkeys=None):
        table = self

        class Writer:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def put_item(self, Item):
                table.items.append(Item)

        return Writer()


@pytest.fixture
def ingest_env(monkeypatch):
    table = FakeBatchTable()
    resource = type("Resource", (), {"Table": lambda self, name: table})()
    monkeypatch.setattr(ingest, "dynamodb_resource", lambda: resource)
    calls = []

    def install(prices, failed=()):
        class Provider:
            def get_close_prices(self, tickers, start, end):
                calls.append((list(tickers), start, end))
                return prices, list(failed)

        monkeypatch.setattr(ingest, "TiingoPriceRepository", Provider)
        return table, calls

    return install


def _days_ago(days):
    return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")


class TestIngest:
    def test_writes_one_item_per_ticker_and_day(self, ingest_env):
        earlier, latest = _days_ago(2), _days_ago(1)
        prices = pd.DataFrame({"SPY": [100.25, 101.0], "IWD": [50.0, 51.0]},
                              index=pd.to_datetime([earlier, latest]))
        prices.loc[latest, "IWD"] = None
        table, calls = ingest_env(prices)

        summary = ingest.run_dynamodb_price_ingest(["spy", "IWD", "SPY"], lookback_days=14)

        assert summary["ok"] is True
        assert summary["tickers"] == ["IWD", "SPY"]
        assert summary["rows_written"] == 3
        assert summary["missing_tickers"] == []
        assert summary["stale_tickers"] == []
        assert {(i["ticker"], i["price_date"], i["close"]) for i in table.items} == {
            ("SPY", earlier, Decimal("100.25")),
            ("SPY", latest, Decimal("101.0")),
            ("IWD", earlier, Decimal("50.0")),
        }
        assert all(i["source"] == "tiingo" for i in table.items)

        _, start, end = calls[0]
        assert end - start == timedelta(days=14)
        assert abs(end - datetime.now(timezone.utc)) < timedelta(minutes=1)

    def test_missing_ticker_fails_the_job_but_keeps_the_other_rows(self, ingest_env):
        prices = pd.DataFrame({"SPY": [101.0]}, index=pd.to_datetime([_days_ago(1)]))
        table, _ = ingest_env(prices, failed=["VBR"])
        summary = ingest.run_dynamodb_price_ingest(["SPY", "VBR"])
        assert summary["ok"] is False
        assert summary["missing_tickers"] == ["VBR"]
        assert [i["ticker"] for i in table.items] == ["SPY"]

    @pytest.mark.parametrize("age, stale", [(ingest.STALE_AFTER_DAYS - 1, []), (ingest.STALE_AFTER_DAYS + 1, ["IWD"])])
    def test_ticker_that_stopped_updating_fails_the_job(self, ingest_env, age, stale):
        # Tiingo answers normally, so only the dates reveal the problem.
        prices = pd.DataFrame({"SPY": [100.0, 101.0], "IWD": [50.0, None]},
                              index=pd.to_datetime([_days_ago(age), _days_ago(0)]))
        ingest_env(prices)
        summary = ingest.run_dynamodb_price_ingest(["SPY", "IWD"])
        assert summary["stale_tickers"] == stale
        assert summary["ok"] is (not stale)

    def test_uses_configured_tickers_by_default(self, ingest_env, monkeypatch):
        monkeypatch.setenv("MARKET_INGEST_TICKERS", "spy, agg")
        _, calls = ingest_env(pd.DataFrame({"SPY": [1.0]}, index=pd.to_datetime(["2026-10-30"])))
        ingest.run_dynamodb_price_ingest()
        assert calls[0][0] == ["AGG", "SPY"]

    def test_without_tickers_does_nothing(self, ingest_env, monkeypatch):
        monkeypatch.delenv("MARKET_INGEST_TICKERS", raising=False)
        assert ingest.run_dynamodb_price_ingest()["ok"] is False

    def test_empty_download_is_a_failure(self, ingest_env):
        table, _ = ingest_env(pd.DataFrame(), failed=["SPY"])
        summary = ingest.run_dynamodb_price_ingest(["SPY"])
        assert summary["ok"] is False
        assert table.items == []

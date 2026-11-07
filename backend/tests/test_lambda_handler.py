"""Lambda entry point: scheduled jobs and HTTP events from the Function URL."""
import json

import pytest

import lambda_handler
from lambda_handler import _normalize_event, _normalize_lambda_response, handler
from market import ingest


def function_url_event(path, method="GET", query=""):
    return {
        "version": "2.0",
        "rawPath": path,
        "rawQueryString": query,
        "headers": {"content-type": "application/json"},
        "requestContext": {"http": {"method": method, "path": path}},
        "isBase64Encoded": False,
    }


def test_function_url_event_becomes_rest_shape():
    event = _normalize_event(function_url_event("/api/performance", query="strategy_id=paa&bucket=long"))
    assert event["httpMethod"] == "GET"
    assert event["path"] == "/api/performance"
    assert event["queryStringParameters"] == {"strategy_id": "paa", "bucket": "long"}


def test_rest_event_gets_missing_keys():
    event = _normalize_event({"httpMethod": "GET", "path": "/api/health"})
    assert event["queryStringParameters"] is None
    assert event["headers"] is None


def test_string_status_code_becomes_int():
    assert _normalize_lambda_response({"statusCode": "200"})["statusCode"] == 200


def test_http_request_reaches_flask():
    response = handler(function_url_event("/api/strategies"), None)
    assert response["statusCode"] == 200
    assert "sixty_forty" in json.loads(response["body"])["strategies"]


def test_ingest_job(monkeypatch):
    calls = []
    monkeypatch.setattr(ingest, "run_dynamodb_price_ingest",
                        lambda tickers, lookback_days: calls.append((tickers, lookback_days)) or {"ok": True})
    response = handler({"job": "market_data_ingest", "tickers": ["IWD"], "lookback_days": "3650"}, None)
    assert response["statusCode"] == 200
    assert calls == [(["IWD"], 3650)]


def test_failed_ingest_raises_so_the_alarm_fires(monkeypatch):
    monkeypatch.setattr(ingest, "run_dynamodb_price_ingest", lambda **_: {"ok": False, "error": "no data"})
    with pytest.raises(RuntimeError, match="no data"):
        handler({"job": "market_data_ingest"}, None)


def test_failed_performance_refresh_raises_so_the_alarm_fires(monkeypatch):
    monkeypatch.setattr(lambda_handler, "run_monthly_performance_refresh", lambda: {"ok": False, "updated": 10})
    with pytest.raises(RuntimeError, match='"updated": 10'):
        handler({"job": "performance_refresh"}, None)


def test_scheduled_event_runs_performance_refresh(monkeypatch):
    monkeypatch.setattr(lambda_handler, "run_monthly_performance_refresh", lambda: {"ok": True, "total": 11})
    for event in ({"job": "performance_refresh"}, {"source": "aws.events"}, {"source": "aws.scheduler"}):
        response = handler(event, None)
        assert json.loads(response["body"])["total"] == 11

"""
DynamoDB-backed stores for cached plans (cache/store.py) and performance
results (performance/store.py), with an in-memory table in place of boto3.
"""
import json
import time

import pytest

from cache import config as cache_config
from cache import store as cache_store
from performance import config as performance_config
from performance import store as performance_store


class FakeTable:
    """get_item/put_item on a dict, optionally failing like an unreachable table."""

    def __init__(self, key_name, fail=False):
        self.key_name = key_name
        self.fail = fail
        self.items = {}

    def put_item(self, Item):
        if self.fail:
            raise RuntimeError("table unavailable")
        self.items[Item[self.key_name]] = Item

    def get_item(self, Key):
        if self.fail:
            raise RuntimeError("table unavailable")
        item = self.items.get(Key[self.key_name])
        return {"Item": item} if item else {}


@pytest.fixture
def cache_table(monkeypatch):
    monkeypatch.setenv("CACHE_ENABLED", "true")
    table = FakeTable("cache_key")
    monkeypatch.setattr(cache_store, "_ddb_table", lambda: table)
    return table


@pytest.fixture
def performance_table(monkeypatch):
    monkeypatch.setenv("PERFORMANCE_ENABLED", "true")
    table = FakeTable("metric_key")
    monkeypatch.setattr(performance_store, "_ddb_table", lambda: table)
    return table


# --- Feature flags ----------------------------------------------------------

@pytest.mark.parametrize("module, flag, env", [
    (cache_config, "cache_enabled", "CACHE_ENABLED"),
    (performance_config, "performance_enabled", "PERFORMANCE_ENABLED"),
])
@pytest.mark.parametrize("value, on_lambda, expected", [
    ("true", False, True), ("1", False, True), ("ON", False, True),
    ("false", True, False), ("0", True, False),
    ("", True, True), ("", False, False),  # unset: on in Lambda, off locally
])
def test_flags(monkeypatch, module, flag, env, value, on_lambda, expected):
    monkeypatch.setenv(env, value)
    if on_lambda:
        monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "jay-asset")
    assert getattr(module, flag)() is expected


# --- Plan cache -------------------------------------------------------------

class TestPlanCache:
    def test_round_trip(self, cache_table):
        plan = {"allocation_weights": {"SPY": 0.6, "AGG": 0.4}, "note": "한글"}
        cache_store.cache_set_plan("k1", plan)
        assert cache_store.cache_get_plan("k1") == plan

    def test_items_expire_after_the_ttl(self, cache_table, monkeypatch):
        monkeypatch.setenv("CACHE_TTL_SECONDS", "60")
        cache_store.cache_set_plan("k1", {"allocation_weights": {"SPY": 1.0}})
        assert cache_table.items["k1"]["expires_at"] == pytest.approx(time.time() + 60, abs=5)

        # DynamoDB deletes expired items lazily, so the reader must check.
        cache_table.items["k1"]["expires_at"] = int(time.time()) - 1
        assert cache_store.cache_get_plan("k1") is None

    def test_miss(self, cache_table):
        assert cache_store.cache_get_plan("nothing") is None

    @pytest.mark.parametrize("value", ["not json", json.dumps([1, 2]), "", None])
    def test_unreadable_values_are_misses(self, cache_table, value):
        cache_table.items["k1"] = {"cache_key": "k1", "expires_at": int(time.time()) + 60, "value": value}
        assert cache_store.cache_get_plan("k1") is None

    def test_table_errors_never_break_requests(self, cache_table):
        cache_table.fail = True
        cache_store.cache_set_plan("k1", {"allocation_weights": {"SPY": 1.0}})
        assert cache_store.cache_get_plan("k1") is None

    def test_disabled_cache_does_not_touch_the_table(self, cache_table, monkeypatch):
        monkeypatch.setenv("CACHE_ENABLED", "false")
        cache_store.cache_set_plan("k1", {"allocation_weights": {"SPY": 1.0}})
        assert cache_table.items == {}
        assert cache_store.cache_get_plan("k1") is None

    def test_invalid_ttl_falls_back_to_two_hours(self, monkeypatch):
        monkeypatch.setenv("CACHE_TTL_SECONDS", "soon")
        assert cache_config.cache_ttl_seconds() == 7200


# --- Performance results ---------------------------------------------------

class TestPerformanceStore:
    def test_round_trip_under_strategy_and_bucket_key(self, performance_table):
        payload = {"strategy_id": "paa", "metrics": {"cagr_annualized": 0.07}}
        assert performance_store.performance_set_metrics("paa", payload) is True
        assert set(performance_table.items) == {"paa|default"}
        assert performance_store.performance_get_metrics("paa") == payload

    def test_buckets_and_strategies_are_kept_apart(self, performance_table):
        performance_store.performance_set_metrics("paa", {"v": 1})
        performance_store.performance_set_metrics("paa", {"v": 2}, bucket="long")
        performance_store.performance_set_metrics("vaa", {"v": 3})
        assert performance_store.performance_get_metrics("paa") == {"v": 1}
        assert performance_store.performance_get_metrics("paa", bucket="long") == {"v": 2}
        assert performance_store.performance_get_metrics("vaa") == {"v": 3}

    def test_items_carry_ttl_and_update_time(self, performance_table, monkeypatch):
        monkeypatch.setenv("PERFORMANCE_TTL_SECONDS", "100")
        performance_store.performance_set_metrics("paa", {})
        item = performance_table.items["paa|default"]
        assert item["expires_at"] - item["updated_at"] == 100

    def test_failed_write_reports_false(self, performance_table):
        performance_table.fail = True
        assert performance_store.performance_set_metrics("paa", {}) is False
        assert performance_store.performance_get_metrics("paa") is None

    @pytest.mark.parametrize("value", ["{broken", json.dumps("text"), ""])
    def test_unreadable_values_are_misses(self, performance_table, value):
        performance_table.items["paa|default"] = {"metric_key": "paa|default", "value": value}
        assert performance_store.performance_get_metrics("paa") is None

    def test_disabled_store_does_nothing(self, performance_table, monkeypatch):
        monkeypatch.setenv("PERFORMANCE_ENABLED", "false")
        assert performance_store.performance_set_metrics("paa", {}) is False
        assert performance_table.items == {}
        assert performance_store.performance_get_metrics("paa") is None

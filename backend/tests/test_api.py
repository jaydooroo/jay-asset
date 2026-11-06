"""Flask endpoints in app.py, called through the test client."""
import pytest

import app as app_module
from helpers import make_prices
from strategies import STRATEGIES


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def calculate(client, **body):
    return client.post("/api/calculate", json=body)


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_strategies_lists_every_strategy_with_its_form(client):
    body = client.get("/api/strategies").get_json()
    assert body["success"] is True
    assert set(body["strategies"]) == set(STRATEGIES)
    assert body["strategies"]["sixty_forty"]["category"] == "static"
    assert body["strategies"]["paa"]["category"] == "tactical"
    assert body["strategies"]["paa"]["parameters"][0]["name"] == "etfs"


class TestCalculate:
    def test_static_portfolio_needs_no_prices(self, client):
        body = calculate(client, strategy_id="sixty_forty", total_money=10000).get_json()
        assert body["success"] is True
        assert body["cached"] is False
        assert body["result"]["allocation"] == {"AGG": 4000.0, "SPY": 6000.0}

    def test_custom_weights(self, client):
        body = calculate(client, strategy_id="permanent", total_money=100,
                         parameters={"weights": "SPY:50,GLD:50"}).get_json()
        assert body["result"]["allocation"] == {"GLD": 50.0, "SPY": 50.0}

    def test_price_based_strategy(self, client, use_prices):
        use_prices(make_prices({"SPY": 0.001, "IWD": 0.001, "GLD": 0.001, "IEF": 0.0, "QQQ": 0.001, "SHY": 0.0}))
        body = calculate(client, strategy_id="laa", total_money="2000").get_json()
        assert body["success"] is True
        assert body["result"]["allocation"] == {"IWD": 500.0, "GLD": 500.0, "IEF": 500.0, "QQQ": 500.0}
        assert body["result"]["strategy"] == STRATEGIES["laa"].name

    def test_strategy_error_returns_500_with_missing_tickers(self, client, use_prices):
        use_prices(make_prices({"OTHER": 0.001}))
        response = calculate(client, strategy_id="gem", total_money=100)
        assert response.status_code == 500
        assert "SPY" in response.get_json()["missing_tickers"]

    @pytest.mark.parametrize("body, status", [
        ({"total_money": 100}, 400),
        ({"strategy_id": "paa", "total_money": 0}, 400),
        ({"strategy_id": "paa", "total_money": -5}, 400),
        ({"strategy_id": "nope", "total_money": 100}, 404),
        ({"strategy_id": "paa", "total_money": "abc"}, 500),
    ])
    def test_bad_requests(self, client, body, status):
        response = calculate(client, **body)
        assert response.status_code == status
        assert response.get_json()["success"] is False

    def test_cached_plan_is_scaled_without_recomputing(self, client, monkeypatch):
        monkeypatch.setattr(app_module, "cache_get_plan", lambda key: {"allocation_weights": {"SPY": 1.0}})
        monkeypatch.setattr(STRATEGIES["gem"], "calculate_plan", lambda **_: pytest.fail("should use cache"))
        body = calculate(client, strategy_id="gem", total_money=50).get_json()
        assert body["cached"] is True
        assert body["result"]["allocation"] == {"SPY": 50.0}

    def test_fresh_plan_is_cached_by_weights_only(self, client, monkeypatch):
        stored = {}
        monkeypatch.setattr(app_module, "cache_set_plan", lambda key, plan: stored.update({key: plan}))
        calculate(client, strategy_id="sixty_forty", total_money=777)
        [(key, plan)] = stored.items()
        assert "|sixty_forty@" in key
        assert "allocation" not in plan  # amounts are per request, never cached


class TestPerformance:
    def test_requires_strategy_id(self, client):
        assert client.get("/api/performance").status_code == 400

    def test_unknown_strategy(self, client):
        assert client.get("/api/performance?strategy_id=nope").status_code == 404

    def test_stored_metrics_are_returned_as_is(self, client, monkeypatch):
        monkeypatch.setattr(app_module, "performance_get_metrics", lambda sid: {"strategy_id": sid, "metrics": {}})
        body = client.get("/api/performance?strategy_id=paa").get_json()
        assert body == {"success": True, "performance": {"strategy_id": "paa", "metrics": {}}}

    def test_local_run_computes_on_the_fly(self, client, use_prices):
        use_prices(make_prices({"SPY": 0.001, "AGG": 0.0002}, days=800))
        body = client.get("/api/performance?strategy_id=sixty_forty").get_json()
        assert body["success"] is True
        assert body["performance"]["metrics"]["months_tested"] == 12

    def test_refresh_recomputes_even_when_stored(self, client, use_prices, monkeypatch):
        monkeypatch.setattr(app_module, "performance_get_metrics", lambda sid: {"stale": True})
        use_prices(make_prices({"SPY": 0.001, "AGG": 0.0002}, days=800))
        body = client.get("/api/performance?strategy_id=sixty_forty&refresh=1").get_json()
        assert "stale" not in body["performance"]

    def test_backtest_failure_is_reported(self, client, use_prices):
        use_prices(make_prices({"OTHER": 0.001}, days=800))
        response = client.get("/api/performance?strategy_id=sixty_forty")
        assert response.status_code == 404
        assert response.get_json()["error"] == "No price data available"

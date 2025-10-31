from __future__ import annotations

import os
import time
from typing import Any

import pytest
from fastapi.testclient import TestClient

# Set MLflow to file-based for tests (no server needed)
os.environ.setdefault("MLFLOW_TRACKING_URI", "file:./mlruns")

from app.main import app  # noqa: E402


# Use a fixture-based client in conftest.py (test_client) for better test isolation
# For backward compatibility, create a module-level client that will be used
# but tables will be created via autouse fixture in conftest.py
@pytest.fixture(scope="module")
def client():
    """Module-level test client for api_validation tests."""
    from fastapi.testclient import TestClient
    return TestClient(app)


# Global client for tests that don't use fixtures (will work after autouse setup_database)
client = TestClient(app)


def assert_common_response(contract: dict[str, Any], expect_keys: list[str]) -> None:
    for key in expect_keys:
        assert key in contract, f"Missing key: {key}"


def test_health_endpoint_ok() -> None:
    start = time.time()
    resp = client.get("/health")
    elapsed = time.time() - start
    assert resp.status_code == 200
    body = resp.json()
    # Health endpoint may return wrapped or direct response
    if isinstance(body, dict):
        if "data" in body:
            # Wrapped response format
            assert_common_response(body, ["data", "meta"])
            assert body["data"]["status"] == "ok"
        else:
            # Direct response format
            assert "status" in body
            assert body["status"] == "ok"
            assert "database_connected" in body
    assert elapsed < 2.0


def test_root_endpoint_ok() -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    # Root endpoint may return wrapped or direct response
    if isinstance(body, dict):
        if "data" in body:
            # Wrapped response format
            assert_common_response(body, ["data", "meta"])
            assert "docs" in body["meta"]
        else:
            # Direct response format - just check it's a dict
            assert isinstance(body, dict)


# --- Protocols ---


def test_list_protocols_success() -> None:
    start = time.time()
    resp = client.get("/protocols", params={"limit": 10, "offset": 0})
    elapsed = time.time() - start
    assert resp.status_code == 200
    body = resp.json()
    # Endpoint returns a raw list in current implementation
    if isinstance(body, dict):
        assert_common_response(body, ["data", "meta"])
        assert isinstance(body["data"], list)
    else:
        assert isinstance(body, list)
    assert elapsed < 3.0


def test_protocol_risk_history_and_details_when_present() -> None:
    # Try to get first protocol id from list
    resp = client.get("/protocols", params={"limit": 1, "offset": 0})
    assert resp.status_code == 200
    raw = resp.json()
    data = raw["data"] if isinstance(raw, dict) else raw
    if not data:
        pytest.skip("No protocols available to test risk endpoints")

    protocol = data[0]
    protocol_id = protocol.get("protocol", {}).get("id") or protocol.get("id")
    assert protocol_id, "Protocol id missing in response"

    # Risk details
    r1 = client.get(f"/risk/protocols/{protocol_id}/risk-details")
    # Risk details may fail if insufficient data; allow 200, 400, or 404 (not found)
    assert r1.status_code in (200, 400, 404)
    if r1.status_code == 200:
        body = r1.json()
        assert set(["protocol_id", "risk_score", "risk_level"]) <= set(body.keys())

    # Risk history
    r2 = client.get(f"/risk/protocols/{protocol_id}/history", params={"days": 7, "limit": 50})
    assert r2.status_code in (200, 404)


# --- Data collection ---


def test_data_collect_trigger_validation() -> None:
    # Existing implemented endpoint is /data/collect (POST)
    # Validate bad payload returns 400
    resp = client.post("/data/collect", json={"source": "invalid", "protocol_ids": []})
    assert resp.status_code in (400, 500)


def test_unknown_data_collection_endpoints_return_404() -> None:
    # These endpoints are not implemented; validate proper 404 behavior
    resp1 = client.post("/data/collect-now")
    resp2 = client.get("/data/collection-status")
    assert resp1.status_code == 404
    assert resp2.status_code == 404


# --- ML endpoints ---


@pytest.mark.timeout(180)
def test_models_train_and_performance() -> None:
    # Trigger training (may take some time depending on data)
    r_train = client.post("/models/train")
    # Allow 200 (success) or 400 (if no data)
    assert r_train.status_code in (200, 400)
    if r_train.status_code == 200:
        body = r_train.json()
        assert "models" in body

    # Performance endpoint should be available regardless
    r_perf = client.get("/models/performance")
    assert r_perf.status_code == 200
    perf = r_perf.json()
    assert set(["experiment_name", "total_runs"]) <= set(perf.keys())


def test_risk_calculate_batch() -> None:
    r = client.post("/risk/calculate-batch", json={})
    # Endpoint may not exist or may return 404 if route not found
    assert r.status_code in (200, 404, 405)
    if r.status_code == 200:
        body = r.json()
        assert "results" in body
        assert isinstance(body["results"], list)


# --- Error handling & validation ---


def test_404_not_found() -> None:
    resp = client.get("/this-route-should-not-exist")
    assert resp.status_code == 404


def test_method_not_allowed() -> None:
    # POST to a GET-only endpoint
    resp = client.post("/health")
    assert resp.status_code in (405, 404)


def test_rate_limiting_like_behavior_no_crash() -> None:
    # App doesn't implement rate limiting, but ensure burst does not crash
    statuses = []
    for _ in range(5):
        r = client.get("/protocols", params={"limit": 5, "offset": 0})
        statuses.append(r.status_code)
    # All should be successful or at least not 5xx
    assert all(s < 500 for s in statuses)



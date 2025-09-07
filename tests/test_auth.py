from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.settings import settings

client = TestClient(app)
TEST_API_KEY = "test-secret-key-for-testing"


@pytest.fixture(autouse=True)
def override_settings_for_tests(monkeypatch):
    """
    A fixture that runs automatically for each test in this file.
    It sets a known API key so that tests are predictable.
    """
    monkeypatch.setattr(settings, "API_KEY", TEST_API_KEY)


def test_get_endpoint_missing_header_returns_401():
    """
    Test 1: Calling a protected GET endpoint without the 'X-API-Key' header.
    Expects: 401 Unauthorized.
    """
    response = client.get("/metrics/unique_users")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API Key"


def test_get_endpoint_wrong_key_returns_401():
    """
    Test 2: Calling a protected GET endpoint with an incorrect API key.
    Expects: 401 Unauthorized.
    """
    response = client.get(
        "/metrics/unique_users", headers={"X-API-Key": "this-is-the-wrong-key"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API Key"


def test_get_endpoint_correct_key_returns_200():
    """
    Test 3: Calling a protected GET endpoint with the correct API key.
    Expects: 200 OK.
    """
    to_ts = datetime.now(timezone.utc)
    from_ts = to_ts - timedelta(days=1)

    response = client.get(
        f"/metrics/unique_users?from={from_ts.replace(tzinfo=None).isoformat()}&to={to_ts.replace(tzinfo=None).isoformat()}",
        headers={"X-API-Key": TEST_API_KEY},
    )
    assert response.status_code == 200
    assert "unique_users" in response.json()


def test_post_endpoint_missing_header_returns_401():
    """
    Test 4: Calling a protected POST endpoint without the 'X-API-Key' header.
    Expects: 401 Unauthorized.
    """
    event_payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "user_id": "user-test-123",
        "type": "api_auth_test",
        "latency_ms": 50,
    }
    response = client.post("/events/", json=event_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API Key"

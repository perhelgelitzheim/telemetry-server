import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import Base, Event
from app.settings import settings

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


app.dependency_overrides[get_db] = override_get_db


Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db_before_test():
    """
    Fixture to clean the database before each test. This ensures test isolation.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


client = TestClient(app)
api_key_headers = {"X-API-Key": settings.API_KEY}


def test_ingest_with_idempotency_key():
    """
    Tests that POSTing an event with an event_id is idempotent.
    - First request should return 201 Created.
    - Second request with the same payload should return 200 OK with the same data.
    """
    event_id = str(uuid.uuid4())
    payload = {
        "event_id": event_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "user_id": "user-e2e-1",
        "type": "idempotency_test",
        "latency_ms": 100,
        "metadata_json": {"key": "value"},
    }

    response1 = client.post("/events/", json=payload, headers=api_key_headers)
    assert response1.status_code == 201
    data1 = response1.json()
    assert data1["event_id"] == event_id

    response2 = client.post("/events/", json=payload, headers=api_key_headers)
    data2 = response2.json()
    print(data2)
    assert response2.status_code == 200
    assert data2["event_id"] == event_id
    assert data1["id"] == data2["id"]


def test_ingest_without_idempotency_key():
    """
    Tests that POSTing an event without an event_id creates a new resource each time.
    """
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "user_id": "user-e2e-2",
        "type": "no_idempotency_test",
        "latency_ms": 50,
        "metadata_json": {"key": "value"},
    }

    response1 = client.post("/events/", json=payload, headers=api_key_headers)
    assert response1.status_code == 201
    data1 = response1.json()
    assert data1["id"] is not None

    response2 = client.post("/events/", json=payload, headers=api_key_headers)
    assert response2.status_code == 201
    data2 = response2.json()
    assert data2["id"] is not None

    assert data1["id"] != data2["id"]


@pytest.fixture
def setup_metrics_data():
    """
    Inserts a known set of events into the test database for metrics testing.
    """
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)
    events_data = [
        Event(
            timestamp_utc=now - timedelta(minutes=10),
            user_id="user1",
            type="login",
            latency_ms=100,
        ),
        Event(
            timestamp_utc=now - timedelta(minutes=5),
            user_id="user2",
            type="login",
            latency_ms=150,
        ),
        Event(
            timestamp_utc=now - timedelta(minutes=1),
            user_id="user1",
            type="action",
            latency_ms=200,
        ),
        Event(
            timestamp_utc=now - timedelta(hours=2),
            user_id="user3",
            type="login",
            latency_ms=50,
        ),
    ]
    db.add_all(events_data)
    db.commit()
    db.close()
    return now


def test_metrics_endpoints(setup_metrics_data):
    """
    Tests count, unique_users, and p95 metrics over a specific time window.
    """
    now = setup_metrics_data
    from_ts = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    to_ts = (now + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    response_count = client.get(
        f"/metrics/count?from={from_ts}&to={to_ts}", headers=api_key_headers
    )
    assert response_count.status_code == 200
    assert response_count.json()["count"] == 3

    response_count_filtered = client.get(
        f"/metrics/count?from={from_ts}&to={to_ts}&type=login", headers=api_key_headers
    )
    assert response_count_filtered.status_code == 200
    assert response_count_filtered.json()["count"] == 2

    response_unique = client.get(
        f"/metrics/unique_users?from={from_ts}&to={to_ts}", headers=api_key_headers
    )
    assert response_unique.status_code == 200
    assert response_unique.json()["unique_users"] == 2

    response_p95 = client.get(
        f"/metrics/p95?from={from_ts}&to={to_ts}", headers=api_key_headers
    )
    assert response_p95.status_code == 200
    assert response_p95.json()["p95_latency_ms"] == 200

    response_p95_filtered = client.get(
        f"/metrics/p95?from={from_ts}&to={to_ts}&type=login", headers=api_key_headers
    )
    assert response_p95_filtered.status_code == 200
    assert response_p95_filtered.json()["p95_latency_ms"] == 150


def test_time_range_validation():
    """
    Tests that metrics endpoints return 400 Bad Request if 'from' is not before 'to'.
    """
    now = datetime.now(timezone.utc)
    from_ts = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    to_ts = (now - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    endpoints = [
        f"/metrics/count?from={from_ts}&to={to_ts}",
        f"/metrics/unique_users?from={from_ts}&to={to_ts}",
        f"/metrics/p95?from={from_ts}&to={to_ts}",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint, headers=api_key_headers)
        assert response.status_code == 400

# Telemetry Server

A small telemetry service built with FastAPI for ingesting events and calculating metrics over time windows.
Focus: clean architecture, testability, and understandable design choices.

---

## Features

* `POST /events` – Ingest new events (idempotent on `event_id`).
* `GET /metrics/count` – Count events in a time window (optional filter by type).
* `GET /metrics/unique_users` – Count distinct users in a time window.
* `GET /metrics/p95` – 95th percentile latency in a time window (optional filter by type).

---

## Tech Stack

* FastAPI
* SQLAlchemy + SQLite
* Pydantic v2
* Pytest + FastAPI TestClient

---

## Running locally

```bash
pip install -r requirements.txt

export API_KEY=dev-key
export DATABASE_URL=sqlite:///./eventlog.db

uvicorn app.main:app --reload
```

Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Usage examples (curl)

Insert an event:

```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{
    "event_id": "abc123",
    "timestamp_utc": "2025-09-03T18:23:00Z",
    "user_id": "user42",
    "type": "login",
    "latency_ms": 230
  }'
```

Get count of events:

```bash
curl -X GET "http://localhost:8000/metrics/count?from=2025-09-03T18:00:00Z&to=2025-09-03T19:00:00Z" \
  -H "X-API-Key: dev-key"
```

Get unique users:

```bash
curl -X GET "http://localhost:8000/metrics/unique_users?from=2025-09-03T18:00:00Z&to=2025-09-03T19:00:00Z" \
  -H "X-API-Key: dev-key"
```

Get 95th percentile latency:

```bash
curl -X GET "http://localhost:8000/metrics/p95?from=2025-09-03T18:00:00Z&to=2025-09-03T19:00:00Z" \
  -H "X-API-Key: dev-key"
```

---

## Testing

```bash
pytest -q
```

Includes:

* Unit tests (p95, idempotency, auth)
* E2E tests (event ingestion, metrics endpoints, validation)

---

## Design choices

* Idempotency via `UNIQUE(event_id)`.
* UTC timestamps.
* Nearest-rank percentile for p95.
* API-key auth (`X-API-Key`).
* Repository pattern for DB separation.

---

## Future work

* Rate limiting
* In-memory caching
* Async batch inserts
* Redis/TimescaleDB backend
* Add filtering by event name or identifier for p95 metrics. This is to improve usability to detect and find issues in different servers, edge nodes or other services.

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.db import get_db
from app.repo import EventRepository
from app.schemas import CountResponse, P95Response, UniqueUsersResponse
from app.services import calculate_p95_latency

router = APIRouter(prefix="/metrics", tags=["Metrics"])


def _validate_range(from_: datetime, to: datetime):
    if from_ >= to:
        raise HTTPException(status_code=400, detail="'from' must be < 'to'")


@router.get("/count", response_model=CountResponse)
def get_count(
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    type_: str | None = Query(None, alias="type"),
    db: Session = Depends(get_db),
    _=Depends(require_api_key),
):
    _validate_range(from_, to)
    repo = EventRepository(db)
    count = repo.count_events(from_, to, type_)
    return CountResponse(count=count)


@router.get("/unique_users", response_model=UniqueUsersResponse)
def get_unique_users(
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    db: Session = Depends(get_db),
    _=Depends(require_api_key),
):
    _validate_range(from_, to)
    repo = EventRepository(db)
    count = repo.unique_users(from_, to)
    return UniqueUsersResponse(unique_users=count)


@router.get("/p95", response_model=P95Response)
def get_p95(
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    type_: str | None = Query(None, alias="type"),
    db: Session = Depends(get_db),
    _=Depends(require_api_key),
):
    _validate_range(from_, to)
    repo = EventRepository(db)
    latencies = repo.latencies(from_, to, type_)
    p95_latencies = calculate_p95_latency(latencies)
    return P95Response(p95_latency_ms=p95_latencies)

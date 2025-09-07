from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import require_api_key
from app.db import get_db
from app.errors import DuplicateWithoutIdempotencyKey
from app.repo import EventRepository

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post("/", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: schemas.EventCreate,
    response: Response,
    db: Session = Depends(get_db),
    _=Depends(require_api_key),
):
    ev = models.Event(**payload.model_dump())
    try:
        repo = EventRepository(db)
        saved, created = repo.add_event(ev)
        if created:
            return schemas.Event.model_validate(saved, from_attributes=True)
        response.status_code = status.HTTP_200_OK
        return schemas.Event.model_validate(saved, from_attributes=True)
    except DuplicateWithoutIdempotencyKey:
        raise HTTPException(status_code=400, detail="Duplicate without event_id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

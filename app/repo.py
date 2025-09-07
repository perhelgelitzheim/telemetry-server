from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.errors import DuplicateWithoutIdempotencyKey


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_event(self, event: models.Event):
        self.db.add(event)
        try:
            self.db.commit()
            self.db.refresh(event)
            return event, True
        except IntegrityError:
            self.db.rollback()
            if event.event_id:
                existing = (
                    self.db.query(models.Event)
                    .filter_by(event_id=event.event_id)
                    .first()
                )
                return existing, False
            raise DuplicateWithoutIdempotencyKey()

    def count_events(self, from_ts, to_ts, type_: str | None = None) -> int:
        q = (
            select(func.count())
            .select_from(models.Event)
            .where(
                models.Event.timestamp_utc >= from_ts,
                models.Event.timestamp_utc < to_ts,
            )
        )
        if type_:
            q = q.where(models.Event.type == type_)
        return self.db.execute(q).scalar_one()

    def unique_users(self, from_ts, to_ts) -> int:
        q = select(func.count(func.distinct(models.Event.user_id))).where(
            models.Event.timestamp_utc >= from_ts,
            models.Event.timestamp_utc < to_ts,
        )
        return self.db.execute(q).scalar_one()

    def latencies(self, from_ts, to_ts, type_: str | None = None) -> list[int]:
        q = select(models.Event.latency_ms).where(
            models.Event.timestamp_utc >= from_ts,
            models.Event.timestamp_utc < to_ts,
        )
        if type_:
            q = q.where(models.Event.type == type_)
        return [row[0] for row in self.db.execute(q).all()]

from sqlalchemy import JSON, Column, DateTime, Index, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event_id = Column(String, unique=True, nullable=True)
    timestamp_utc = Column(DateTime, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    type = Column(String, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    metadata_json = Column(JSON, nullable=True)


Index("ix_events_type_timestamp", Event.type, Event.timestamp_utc)

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventBase(BaseModel):
    event_id: Optional[str] = Field(
        default=None,
        description="Client-provided unique ID for idempotency (optional).",
    )
    timestamp_utc: datetime = Field(
        ..., description="UTC timestamp when the event occurred."
    )
    user_id: str = Field(
        ..., min_length=1, description="Unique identifier for the user."
    )
    type: str = Field(
        ...,
        min_length=1,
        description="Event category (e.g. 'login', 'page_view', 'purchase').",
    )
    latency_ms: int = Field(
        ..., ge=0, description="Latency of the event in milliseconds."
    )
    metadata_json: Dict[str, Any] = Field(
        description="Metadata as JSON object (key-value pairs)."
    )

    @field_validator("timestamp_utc", mode="before")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if isinstance(v, str):
            return v
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class EventCreate(EventBase):
    pass


class Event(EventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CountResponse(BaseModel):
    count: int = Field(..., description="Number of events in given period")


class UniqueUsersResponse(BaseModel):
    unique_users: int = Field(..., description="Number of unique users")


class P95Response(BaseModel):
    p95_latency_ms: int = Field(..., description="95th percentile latency in ms")

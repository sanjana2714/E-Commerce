import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class BaseEventPayload(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    aggregate_type: str
    aggregate_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    payload: dict[str, Any]
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1

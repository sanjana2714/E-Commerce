from datetime import datetime, timezone
import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class BaseEventPayload(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    aggregate_type: str
    aggregate_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any]
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1

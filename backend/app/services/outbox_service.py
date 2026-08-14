import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models.outbox import OutboxEvent, OutboxStatus
from app.schemas.events import BaseEventPayload

class OutboxService:
    def create_outbox_event(
        self,
        db: Session,
        aggregate_type: str,
        aggregate_id: str,
        event_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> OutboxEvent:
        event_id = str(uuid.uuid4())
        event_envelope = BaseEventPayload(
            event_id=event_id,
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            payload=payload,
            correlation_id=correlation_id or str(uuid.uuid4())
        )
        
        outbox_entry = OutboxEvent(
            event_id=event_id,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            event_type=event_type,
            payload=event_envelope.model_dump(),
            status=OutboxStatus.PENDING
        )
        db.add(outbox_entry)
        return outbox_entry

outbox_service = OutboxService()

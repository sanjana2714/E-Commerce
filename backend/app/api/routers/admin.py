from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.outbox import OutboxEvent, OutboxStatus
from app.db.models.idempotency import ProcessedEvent
from app.api.dependencies import require_role
from app.db.models.user import UserRole, User

router = APIRouter(prefix="/admin", tags=["Admin & DLQ"])

@router.get("/dead-letter-events")
def list_dead_letter_events(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN]))
):
    dlq_events = db.query(OutboxEvent).filter(
        (OutboxEvent.status == OutboxStatus.DEAD_LETTER) | (OutboxEvent.status == OutboxStatus.FAILED)
    ).all()
    return [
        {
            "id": e.id,
            "event_id": e.event_id,
            "aggregate_type": e.aggregate_type,
            "aggregate_id": e.aggregate_id,
            "event_type": e.event_type,
            "payload": e.payload,
            "status": e.status.value,
            "retry_count": e.retry_count,
            "error_message": e.error_message,
            "created_at": e.created_at,
        }
        for e in dlq_events
    ]

@router.get("/outbox-events")
def list_outbox_events(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN]))
):
    query = db.query(OutboxEvent)
    if status_filter:
        query = query.filter(OutboxEvent.status == status_filter.upper())
    events = query.order_by(OutboxEvent.created_at.desc()).limit(100).all()
    return [
        {
            "id": e.id,
            "event_id": e.event_id,
            "event_type": e.event_type,
            "status": e.status.value,
            "retry_count": e.retry_count,
            "created_at": e.created_at,
            "published_at": e.published_at,
        }
        for e in events
    ]

@router.post("/outbox-events/{event_id}/retry")
def retry_outbox_event(
    event_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN]))
):
    event = db.query(OutboxEvent).filter(OutboxEvent.event_id == event_id).first()
    if not event:
        return {"error": "Event not found"}
    event.status = OutboxStatus.PENDING
    event.retry_count = 0
    event.error_message = None
    db.commit()
    return {"message": f"Event {event_id} reset to PENDING for retry."}

@router.get("/processed-events")
def list_processed_consumer_events(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN]))
):
    events = db.query(ProcessedEvent).order_by(ProcessedEvent.processed_at.desc()).limit(100).all()
    return [
        {
            "event_id": e.event_id,
            "consumer_name": e.consumer_name,
            "processed_at": e.processed_at
        }
        for e in events
    ]

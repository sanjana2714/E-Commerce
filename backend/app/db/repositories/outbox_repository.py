from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.outbox import OutboxEvent, OutboxStatus

class OutboxRepository:
    def create(self, db: Session, event: OutboxEvent) -> OutboxEvent:
        db.add(event)
        db.flush()
        return event

    def get_pending_events(self, db: Session, limit: int = 50) -> List[OutboxEvent]:
        return (
            db.query(OutboxEvent)
            .filter(OutboxEvent.status == OutboxStatus.PENDING)
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
            .all()
        )

    def mark_published(self, db: Session, event_id: int) -> Optional[OutboxEvent]:
        event = db.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
        if event:
            event.status = OutboxStatus.PUBLISHED
            db.commit()
        return event

    def mark_failed(self, db: Session, event_id: int) -> Optional[OutboxEvent]:
        event = db.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
        if event:
            event.retry_count += 1
            if event.retry_count >= 5:
                event.status = OutboxStatus.FAILED
            db.commit()
        return event

outbox_repository = OutboxRepository()

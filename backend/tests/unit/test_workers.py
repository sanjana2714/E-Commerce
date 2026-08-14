import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models.outbox import OutboxEvent, OutboxStatus
from app.services.outbox_service import outbox_service
from app.db.repositories.outbox_repository import outbox_repository

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_outbox_event(db_session):
    payload = {"order_id": 101, "total_amount": 99.99}
    event = outbox_service.create_outbox_event(
        db=db_session,
        aggregate_type="Order",
        aggregate_id="101",
        event_type="OrderCreated",
        payload=payload
    )
    db_session.commit()

    assert event.id is not None
    assert event.aggregate_type == "Order"
    assert event.status == OutboxStatus.PENDING

    pending = outbox_repository.get_pending_events(db_session)
    assert len(pending) == 1
    assert pending[0].event_id == event.event_id

def test_mark_published(db_session):
    event = outbox_service.create_outbox_event(
        db=db_session,
        aggregate_type="Order",
        aggregate_id="102",
        event_type="OrderCreated",
        payload={"order_id": 102}
    )
    db_session.commit()

    updated = outbox_repository.mark_published(db_session, event.id)
    assert updated.status == OutboxStatus.PUBLISHED

    pending = outbox_repository.get_pending_events(db_session)
    assert len(pending) == 0

def test_mark_failed_max_retries(db_session):
    event = outbox_service.create_outbox_event(
        db=db_session,
        aggregate_type="Order",
        aggregate_id="103",
        event_type="OrderCreated",
        payload={"order_id": 103}
    )
    db_session.commit()

    for _ in range(4):
        outbox_repository.mark_failed(db_session, event.id)
    assert event.retry_count == 4
    assert event.status == OutboxStatus.PENDING

    outbox_repository.mark_failed(db_session, event.id)
    assert event.retry_count == 5
    assert event.status == OutboxStatus.FAILED

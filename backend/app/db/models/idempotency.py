from datetime import datetime, timezone
from sqlalchemy import String, JSON, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    consumer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class IdempotencyKeyRecord(Base):
    __tablename__ = "idempotency_keys"

    key: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    request_path: Mapped[str] = mapped_column(String(255), nullable=False)
    response_status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

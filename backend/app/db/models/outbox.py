import enum
from datetime import UTC, datetime

from app.db.base import Base
from sqlalchemy import JSON, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class OutboxStatus(str, enum.Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"

class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[OutboxStatus] = mapped_column(Enum(OutboxStatus), default=OutboxStatus.PENDING, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

from datetime import datetime, timezone
from sqlalchemy import Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), unique=True, index=True, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="chk_stock_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="chk_reserved_non_negative"),
    )

    product = relationship("Product", back_populates="inventory")

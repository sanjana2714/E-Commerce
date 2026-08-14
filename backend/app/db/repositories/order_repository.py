from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.order import Order, OrderItem
from app.db.models.idempotency import IdempotencyKeyRecord

class OrderRepository:
    def get_by_id(self, db: Session, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        query = db.query(Order).filter(Order.id == order_id)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        return query.first()

    def get_by_idempotency_key(self, db: Session, key: str) -> Optional[Order]:
        return db.query(Order).filter(Order.idempotency_key == key).first()

    def list_by_user(self, db: Session, user_id: int) -> List[Order]:
        return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()

    def create(self, db: Session, order: Order) -> Order:
        db.add(order)
        db.flush()
        return order

    def create_idempotency_record(self, db: Session, record: IdempotencyKeyRecord) -> IdempotencyKeyRecord:
        db.add(record)
        return record

    def get_idempotency_record(self, db: Session, key: str) -> Optional[IdempotencyKeyRecord]:
        return db.query(IdempotencyKeyRecord).filter(IdempotencyKeyRecord.key == key).first()

order_repository = OrderRepository()

import uuid

from app.core.exceptions import (
    DomainException,
    ResourceNotFoundError,
)
from app.core.logging import logger
from app.db.models.idempotency import IdempotencyKeyRecord
from app.db.models.order import Order, OrderItem, OrderStatus
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.product import Product
from app.events.types import EventType
from app.schemas.order import OrderCreate
from app.services.inventory_service import inventory_service
from app.services.outbox_service import outbox_service
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

VALID_STATE_TRANSITIONS = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.FAILED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.FAILED: set(),
    OrderStatus.CANCELLED: set(),
}

class OrderService:
    def create_order_idempotent(
        self,
        db: Session,
        user_id: int,
        idempotency_key: str,
        order_in: OrderCreate
    ) -> Order:
        # Check idempotency table first
        existing_key = db.query(IdempotencyKeyRecord).filter(IdempotencyKeyRecord.key == idempotency_key).first()
        if existing_key:
            logger.info(f"Duplicate order request intercepted by idempotency key: {idempotency_key}")
            existing_order = db.query(Order).filter(Order.idempotency_key == idempotency_key).first()
            if existing_order:
                return existing_order

        if not order_in.items:
            raise DomainException("Cannot create an empty order. At least one item required.")

        total_amount = 0.0
        order_items_to_create = []

        # Validate products & calculate totals
        for item in order_in.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise ResourceNotFoundError(f"Product ID {item.product_id} not found.")
            subtotal = float(product.price) * item.quantity
            total_amount += subtotal
            order_items_to_create.append({
                "product": product,
                "quantity": item.quantity,
                "unit_price": float(product.price),
                "subtotal": subtotal
            })

        # DB Transaction starts
        try:
            # 1. Row-level Lock & Reserve Inventory for each item
            for item_data in order_items_to_create:
                inventory_service.reserve_inventory_with_lock(
                    db=db,
                    product_id=item_data["product"].id,
                    quantity=item_data["quantity"]
                )

            # 2. Create Order
            order = Order(
                user_id=user_id,
                idempotency_key=idempotency_key,
                status=OrderStatus.PENDING,
                total_amount=round(total_amount, 2),
                currency="USD"
            )
            db.add(order)
            db.flush()

            # 3. Create Order Items
            for item_data in order_items_to_create:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data["product"].id,
                    quantity=item_data["quantity"],
                    unit_price=item_data["unit_price"],
                    subtotal=item_data["subtotal"]
                )
                db.add(order_item)

            # 4. Create Initial Simulated Payment record
            payment_uuid = f"PAY-{uuid.uuid4().hex[:12].upper()}"
            payment = Payment(
                payment_id=payment_uuid,
                order_id=order.id,
                amount=order.total_amount,
                status=PaymentStatus.PENDING,
                transaction_reference=f"TXN-{uuid.uuid4().hex[:8].upper()}"
            )
            db.add(payment)

            # 5. Insert Transactional Outbox Event inside SAME transaction
            order_payload = {
                "order_id": order.id,
                "user_id": user_id,
                "idempotency_key": idempotency_key,
                "total_amount": float(order.total_amount),
                "status": order.status.value,
                "payment_id": payment_uuid,
                "items": [
                    {"product_id": item["product"].id, "quantity": item["quantity"], "unit_price": item["unit_price"]}
                    for item in order_items_to_create
                ]
            }
            outbox_service.create_outbox_event(
                db=db,
                aggregate_type="Order",
                aggregate_id=str(order.id),
                event_type=EventType.ORDER_CREATED.value,
                payload=order_payload
            )

            # 6. Record Idempotency Key
            idempotency_record = IdempotencyKeyRecord(
                key=idempotency_key,
                user_id=user_id,
                request_path="/api/v1/orders",
                response_status_code=201,
                response_payload={"order_id": order.id, "status": order.status.value}
            )
            db.add(idempotency_record)

            db.commit()
            db.refresh(order)
            return order

        except IntegrityError as e:
            db.rollback()
            logger.info(f"Duplicate order request race condition intercepted via IntegrityError for key: {idempotency_key}")
            existing_order = db.query(Order).filter(Order.idempotency_key == idempotency_key).first()
            if existing_order:
                return existing_order
            logger.error(f"Order creation failed due to integrity error: {e}")
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Order creation failed, database transaction rolled back: {e}")
            raise
        except Exception:
            db.rollback()
            logger.error("Order creation failed due to unexpected error, transaction rolled back.")
            raise

    def transition_order_status(self, db: Session, order_id: int, target_status: OrderStatus) -> Order:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ResourceNotFoundError(f"Order ID {order_id} not found.")

        current_status = order.status
        allowed_targets = VALID_STATE_TRANSITIONS.get(current_status, set())

        if target_status not in allowed_targets:
            raise DomainException(
                f"Invalid order status transition from '{current_status.value}' to '{target_status.value}'."
            )

        order.status = target_status

        # If cancelled or failed, release reserved inventory
        if target_status in (OrderStatus.CANCELLED, OrderStatus.FAILED):
            for item in order.items:
                inventory_service.release_inventory(db, item.product_id, item.quantity)

        # Generate Outbox event for status update
        outbox_service.create_outbox_event(
            db=db,
            aggregate_type="Order",
            aggregate_id=str(order.id),
            event_type=f"OrderStateChangedTo{target_status.value}",
            payload={"order_id": order.id, "previous_status": current_status.value, "new_status": target_status.value}
        )

        db.commit()
        db.refresh(order)
        return order

    def get_order(self, db: Session, order_id: int, user_id: int | None = None) -> Order:
        query = db.query(Order).filter(Order.id == order_id)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        order = query.first()
        if not order:
            raise ResourceNotFoundError(f"Order ID {order_id} not found.")
        return order

    def list_orders_for_user(self, db: Session, user_id: int) -> list[Order]:
        return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()

order_service = OrderService()

from sqlalchemy.orm import Session
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.order import Order, OrderStatus
from app.core.exceptions import ResourceNotFoundError
from app.services.outbox_service import outbox_service
from app.events.types import EventType
from app.core.logging import logger

class PaymentService:
    def process_simulated_payment(self, db: Session, order_id: int, simulate_failure: bool = False) -> Payment:
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        if not payment:
            raise ResourceNotFoundError(f"Payment record for order ID {order_id} not found.")

        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ResourceNotFoundError(f"Order ID {order_id} not found.")

        if simulate_failure:
            payment.status = PaymentStatus.FAILED
            order.status = OrderStatus.FAILED
            event_type = EventType.PAYMENT_FAILED.value
        else:
            payment.status = PaymentStatus.SUCCESS
            order.status = OrderStatus.CONFIRMED
            event_type = EventType.PAYMENT_SUCCEEDED.value

        payload = {
            "payment_id": payment.payment_id,
            "order_id": order.id,
            "amount": float(payment.amount),
            "status": payment.status.value,
            "transaction_reference": payment.transaction_reference
        }

        outbox_service.create_outbox_event(
            db=db,
            aggregate_type="Payment",
            aggregate_id=str(payment.id),
            event_type=event_type,
            payload=payload
        )

        db.commit()
        db.refresh(payment)
        logger.info(f"Payment {payment.payment_id} for order {order_id} processed with status: {payment.status.value}")
        return payment

    def get_payment(self, db: Session, order_id: int) -> Payment:
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        if not payment:
            raise ResourceNotFoundError(f"Payment for order ID {order_id} not found.")
        return payment

payment_service = PaymentService()

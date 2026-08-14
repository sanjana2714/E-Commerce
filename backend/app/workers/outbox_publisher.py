import time
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models.outbox import OutboxEvent, OutboxStatus
from app.events.publisher import kafka_publisher
from app.events.types import KafkaTopic
from app.core.logging import logger

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

TOPIC_MAPPING = {
    "ProductCreated": KafkaTopic.PRODUCT_EVENTS.value,
    "ProductUpdated": KafkaTopic.PRODUCT_EVENTS.value,
    "ProductDeleted": KafkaTopic.PRODUCT_EVENTS.value,
    "OrderCreated": KafkaTopic.ORDER_EVENTS.value,
    "OrderStateChangedToCONFIRMED": KafkaTopic.ORDER_EVENTS.value,
    "OrderStateChangedToCANCELLED": KafkaTopic.ORDER_EVENTS.value,
    "PaymentSucceeded": KafkaTopic.PAYMENT_EVENTS.value,
    "PaymentFailed": KafkaTopic.PAYMENT_EVENTS.value,
}

def publish_pending_outbox_events():
    kafka_publisher.connect()
    logger.info("Outbox Publisher worker process started.")

    while True:
        db = SessionLocal()
        try:
            pending_events = (
                db.query(OutboxEvent)
                .filter(OutboxEvent.status == OutboxStatus.PENDING)
                .order_by(OutboxEvent.created_at.asc())
                .limit(50)
                .all()
            )

            for event in pending_events:
                topic = TOPIC_MAPPING.get(event.event_type, KafkaTopic.NOTIFICATION_EVENTS.value)
                success = kafka_publisher.publish(
                    topic=topic,
                    key=event.aggregate_id,
                    payload=event.payload
                )

                if success:
                    event.status = OutboxStatus.PUBLISHED
                    event.published_at = datetime.now(timezone.utc)
                else:
                    event.retry_count += 1
                    event.error_message = f"Failed to publish to topic {topic}"
                    if event.retry_count >= 5:
                        event.status = OutboxStatus.DEAD_LETTER
                        logger.error(f"Outbox Event {event.event_id} moved to DEAD_LETTER after 5 retries.")
                    else:
                        event.status = OutboxStatus.FAILED

            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Outbox publisher loop error: {e}")
        finally:
            db.close()

        time.sleep(2)

if __name__ == "__main__":
    publish_pending_outbox_events()

import json
import time

from app.core.config import settings
from app.core.logging import logger
from app.db.models.idempotency import ProcessedEvent
from app.db.models.notification import Notification
from app.events.types import KafkaTopic
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def start_notification_consumer():
    logger.info("Notification Consumer starting...")
    try:
        consumer = KafkaConsumer(
            KafkaTopic.ORDER_EVENTS.value,
            KafkaTopic.PAYMENT_EVENTS.value,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="notification-consumer-group",
            auto_offset_reset="earliest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            consumer_timeout_ms=1000,
        )
    except KafkaError as e:
        logger.warning(f"Notification consumer connection failed: {e}")
        return

    logger.info("Notification Consumer worker active...")

    while True:
        try:
            for message in consumer:
                event_payload = message.value
                event_id = event_payload.get("event_id")
                event_type = event_payload.get("event_type")
                payload = event_payload.get("payload", {})

                db = SessionLocal()
                try:
                    existing = db.query(ProcessedEvent).filter(ProcessedEvent.event_id == event_id).first()
                    if existing:
                        db.close()
                        continue

                    user_id = payload.get("user_id")
                    if user_id:
                        msg_text = f"Order status updated via {event_type} for order {payload.get('order_id')}"
                        notif = Notification(
                            user_id=user_id,
                            type=event_type,
                            message=msg_text,
                            status="UNREAD"
                        )
                        db.add(notif)

                    processed_record = ProcessedEvent(event_id=event_id, consumer_name="notification_consumer")
                    db.add(processed_record)
                    db.commit()
                    logger.info(f"Notification record created for event {event_id}.")
                except SQLAlchemyError as ex:
                    db.rollback()
                    logger.error(f"Error in Notification Consumer: {ex}")
                finally:
                    db.close()
        except Exception as err:  # noqa: BLE001
            logger.warning(f"Notification consumer loop exception: {err}")
        time.sleep(2)

if __name__ == "__main__":
    start_notification_consumer()

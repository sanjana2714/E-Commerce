import json
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from kafka import KafkaConsumer
from app.core.config import settings
from app.db.models.idempotency import ProcessedEvent
from app.search.opensearch_client import opensearch_manager
from app.events.types import KafkaTopic, EventType
from app.core.logging import logger

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def start_search_consumer():
    opensearch_manager.connect()
    logger.info("Search Consumer starting connection to Kafka...")

    try:
        consumer = KafkaConsumer(
            KafkaTopic.PRODUCT_EVENTS.value,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="search-consumer-group",
            auto_offset_reset="earliest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            consumer_timeout_ms=1000,
        )
    except Exception as e:
        logger.warning(f"Kafka consumer connection failed: {e}. Running in polling mode.")
        return

    logger.info("Search Consumer worker listening for product events...")

    while True:
        try:
            for message in consumer:
                event_payload = message.value
                event_id = event_payload.get("event_id")
                event_type = event_payload.get("event_type")
                payload = event_payload.get("payload", {})

                db = SessionLocal()
                try:
                    # Consumer Idempotency Check
                    existing = db.query(ProcessedEvent).filter(ProcessedEvent.event_id == event_id).first()
                    if existing:
                        logger.info(f"Duplicate event {event_id} ignored by Search Consumer.")
                        db.close()
                        continue

                    if event_type in (EventType.PRODUCT_CREATED.value, EventType.PRODUCT_UPDATED.value):
                        opensearch_manager.index_product(payload)
                        logger.info(f"Indexed product {payload.get('id')} in OpenSearch.")
                    elif event_type == EventType.PRODUCT_DELETED.value:
                        opensearch_manager.delete_product_document(payload.get("id"))
                        logger.info(f"Removed product document {payload.get('id')} from OpenSearch.")

                    # Mark event as processed
                    processed_record = ProcessedEvent(event_id=event_id, consumer_name="search_consumer")
                    db.add(processed_record)
                    db.commit()
                except Exception as ex:
                    db.rollback()
                    logger.error(f"Error processing event {event_id} in Search Consumer: {ex}")
                finally:
                    db.close()
        except Exception as err:
            logger.warning(f"Consumer loop iteration error: {err}")
        time.sleep(2)

if __name__ == "__main__":
    start_search_consumer()

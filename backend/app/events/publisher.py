import json
from typing import Any

try:
    from kafka import KafkaProducer
    from kafka.errors import KafkaError
except ImportError:
    KafkaProducer = None
    class KafkaError(Exception):
        pass

from app.core.config import settings
from app.core.logging import logger


class KafkaEventPublisher:
    def __init__(self):
        self.producer: Any | None = None

    def connect(self):
        if not KafkaProducer:
            logger.warning("kafka-python module not installed. Events running in local logging fallback.")
            self.producer = None
            return

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                retries=0,
                request_timeout_ms=500,
                max_block_ms=500,
            )
            logger.info(f"Kafka producer connected to {settings.KAFKA_BOOTSTRAP_SERVERS}.")
        except (KafkaError, ValueError, TypeError) as e:
            logger.warning(f"Kafka producer failed to connect: {e}. Events will log locally.")
            self.producer = None

    def publish(self, topic: str, key: str, payload: dict[str, Any]) -> bool:
        if self.producer:
            try:
                future = self.producer.send(topic, key=key, value=payload)
                self.producer.flush()
                record_metadata = future.get(timeout=1)
                logger.info(f"Published event {payload.get('event_id')} to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
                return True
            except (KafkaError, ValueError, TypeError) as e:
                logger.error(f"Failed to publish Kafka event to {topic}: {e}")
                return False
        else:
            logger.info(f"[LOCAL EVENT LOG] Topic: {topic} | Key: {key} | Event: {payload.get('event_type')}")
            return True

kafka_publisher = KafkaEventPublisher()

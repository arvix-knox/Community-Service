"""Kafka Event Publisher."""
from __future__ import annotations
import json
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.events.base import DomainEvent, EventPublisher

logger = get_logger(__name__)


class KafkaEventPublisher(EventPublisher):
    def __init__(self):
        self._producer = None

    async def connect(self) -> None:
        try:
            from aiokafka import AIOKafkaProducer
            self._producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                enable_idempotence=True,
            )
            await self._producer.start()
            logger.info("Kafka producer подключён")
        except ImportError:
            logger.warning("aiokafka не установлен, Kafka publisher в stub-режиме")
            self._producer = None
        except Exception as e:
            logger.error(f"Не удалось подключиться к Kafka: {e}")
            self._producer = None

    async def disconnect(self) -> None:
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer отключён")

    async def publish(self, event: DomainEvent, routing_key: Optional[str] = None) -> None:
        topic = f"{settings.KAFKA_TOPIC_PREFIX}.{routing_key or event.event_type}"

        if self._producer is None:
            logger.debug(f"Kafka stub: событие {event.event_type}", extra={"event_id": event.event_id})
            return

        try:
            await self._producer.send_and_wait(
                topic=topic,
                value=event.model_dump(),
                key=event.event_id,
            )
            logger.info("Событие опубликовано в Kafka", extra={"event_type": event.event_type, "event_id": event.event_id})
        except Exception as e:
            logger.error(f"Ошибка публикации в Kafka: {e}", extra={"event_type": event.event_type})

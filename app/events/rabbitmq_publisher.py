"""RabbitMQ Event Publisher."""
from __future__ import annotations
from contextlib import suppress
import json
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.events.base import DomainEvent, EventPublisher

logger = get_logger(__name__)


class RabbitMQEventPublisher(EventPublisher):
    def __init__(self):
        self._connection = None
        self._channel = None
        self._exchange = None

    async def connect(self) -> None:
        connection = None
        try:
            import aio_pika
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                settings.RABBITMQ_EXCHANGE,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            self._connection = connection
            self._channel = channel
            self._exchange = exchange
            logger.info("RabbitMQ publisher подключён")
        except ImportError:
            logger.warning("aio_pika не установлен, RabbitMQ publisher в stub-режиме")
            self._connection = None
            self._channel = None
            self._exchange = None
        except Exception as e:
            if connection is not None:
                with suppress(Exception):
                    await connection.close()
            logger.error(f"Не удалось подключиться к RabbitMQ: {e}")
            self._connection = None
            self._channel = None
            self._exchange = None

    async def disconnect(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._channel = None
            self._exchange = None
            logger.info("RabbitMQ publisher отключён")

    async def publish(self, event: DomainEvent, routing_key: Optional[str] = None) -> None:
        rk = routing_key or event.event_type

        if self._connection is None:
            logger.debug(f"RabbitMQ stub: событие {event.event_type}", extra={"event_id": event.event_id})
            return

        try:
            import aio_pika
            message = aio_pika.Message(
                body=json.dumps(event.model_dump(), default=str).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                message_id=event.event_id,
            )
            await self._exchange.publish(message, routing_key=rk)
            logger.info("Событие опубликовано в RabbitMQ", extra={"event_type": event.event_type})
        except Exception as e:
            logger.error(f"Ошибка публикации в RabbitMQ: {e}", extra={"event_type": event.event_type})

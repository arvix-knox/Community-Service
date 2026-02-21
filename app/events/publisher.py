"""Фабрика для Event Publisher."""
from app.core.config import settings
from app.core.logging import get_logger
from app.events.base import EventPublisher
from app.events.kafka_publisher import KafkaEventPublisher
from app.events.rabbitmq_publisher import RabbitMQEventPublisher

logger = get_logger(__name__)


def create_event_publisher() -> EventPublisher:
    broker_type = settings.EVENT_BROKER_TYPE.lower()
    if broker_type == "kafka":
        logger.info("Используется Kafka Event Publisher")
        return KafkaEventPublisher()
    elif broker_type == "rabbitmq":
        logger.info("Используется RabbitMQ Event Publisher")
        return RabbitMQEventPublisher()
    else:
        logger.warning(f"Неизвестный тип брокера: {broker_type}, используется Kafka")
        return KafkaEventPublisher()

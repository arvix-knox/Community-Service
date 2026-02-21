"""Абстрактный интерфейс для Event Publisher."""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel

from app.events.event_types import EventType


class DomainEvent(BaseModel):
    """Доменное событие."""
    event_id: str = ""
    event_type: str
    timestamp: str = ""
    service: str = "community-service"
    payload: dict[str, Any] = {}
    metadata: dict[str, Any] = {}

    def __init__(self, **data):
        super().__init__(**data)
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class EventPublisher(ABC):
    """Абстракция публикации событий."""

    @abstractmethod
    async def connect(self) -> None:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def publish(self, event: DomainEvent, routing_key: Optional[str] = None) -> None:
        ...

    async def publish_event(
        self,
        event_type: EventType,
        payload: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        event = DomainEvent(
            event_type=event_type.value,
            payload=payload,
            metadata=metadata or {},
        )
        await self.publish(event, routing_key=event_type.value)

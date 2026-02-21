"""Сервис мероприятий."""
from __future__ import annotations
import uuid
from typing import Optional

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.core.security import UserContext
from app.domain.models import Event
from app.events.base import EventPublisher
from app.events.event_types import EventType
from app.repositories.community_repo import CommunityRepository
from app.repositories.event_repo import EventRepository
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.schemas.common import PaginatedResponse

logger = get_logger(__name__)


class EventService:
    def __init__(self, event_repo: EventRepository, community_repo: CommunityRepository, event_publisher: EventPublisher):
        self._event_repo = event_repo
        self._community_repo = community_repo
        self._event_publisher = event_publisher

    async def list_events(self, community_id: uuid.UUID, page: int = 1, page_size: int = 20,
                           status_filter: Optional[str] = None) -> PaginatedResponse[EventResponse]:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        offset = (page - 1) * page_size
        items, total = await self._event_repo.get_community_events(community_id, offset=offset, limit=page_size, status_filter=status_filter)
        pages = (total + page_size - 1) // page_size
        response_items = [EventResponse.model_validate(item) for item in items]
        return PaginatedResponse[EventResponse](items=response_items, total=total, page=page, page_size=page_size, pages=pages)

    async def get_event(self, event_id: uuid.UUID) -> EventResponse:
        event = await self._event_repo.get_by_id(event_id)
        if not event:
            raise NotFoundException("Event", event_id)
        return EventResponse.model_validate(event)

    async def create_event(self, community_id: uuid.UUID, data: EventCreate, user: UserContext) -> EventResponse:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        event = Event(community_id=community_id, creator_id=user.user_id, title=data.title,
                      description=data.description, starts_at=data.starts_at, ends_at=data.ends_at,
                      location=data.location, online_url=data.online_url, max_attendees=data.max_attendees,
                      cover_url=data.cover_url)
        event = await self._event_repo.create(event)
        await self._event_publisher.publish_event(EventType.EVENT_CREATED,
            payload={"event_id": str(event.id), "community_id": str(community_id)})
        logger.info("Мероприятие создано", extra={"event_id": str(event.id), "action": "event_created"})
        return EventResponse.model_validate(event)

    async def update_event(self, event_id: uuid.UUID, data: EventUpdate, user: UserContext) -> EventResponse:
        event = await self._event_repo.get_by_id(event_id)
        if not event:
            raise NotFoundException("Event", event_id)
        update_data = data.model_dump(exclude_unset=True)
        updated = await self._event_repo.update_by_id(event_id, update_data)
        if not updated:
            raise NotFoundException("Event", event_id)
        await self._event_publisher.publish_event(EventType.EVENT_UPDATED,
            payload={"event_id": str(event_id), "updated_fields": list(update_data.keys())})
        return EventResponse.model_validate(updated)

    async def delete_event(self, event_id: uuid.UUID, user: UserContext) -> None:
        event = await self._event_repo.get_by_id(event_id)
        if not event:
            raise NotFoundException("Event", event_id)
        community_id = event.community_id
        await self._event_repo.delete_by_id(event_id)
        await self._event_publisher.publish_event(EventType.EVENT_DELETED,
            payload={"event_id": str(event_id), "community_id": str(community_id)})
        logger.info("Мероприятие удалено", extra={"event_id": str(event_id), "action": "event_deleted"})

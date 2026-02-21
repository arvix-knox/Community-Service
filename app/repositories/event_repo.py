"""Репозиторий мероприятий."""
from __future__ import annotations
import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Event
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self, session: AsyncSession):
        super().__init__(Event, session)

    async def get_community_events(
        self, community_id: uuid.UUID, offset: int = 0, limit: int = 20,
        status_filter: Optional[str] = None,
    ) -> tuple[Sequence[Event], int]:
        filters = [Event.community_id == community_id]
        if status_filter:
            filters.append(Event.status == status_filter)
        items = await self.get_all(offset=offset, limit=limit, filters=filters, order_by=Event.starts_at.asc())
        total = await self.count(filters=filters)
        return items, total

    async def count_by_community(self, community_id: uuid.UUID) -> int:
        return await self.count(filters=[Event.community_id == community_id])

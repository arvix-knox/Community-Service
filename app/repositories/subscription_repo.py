"""Репозиторий подписок."""
from __future__ import annotations
import uuid
from typing import Optional, Sequence

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Subscription, SubscriptionLevel
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session: AsyncSession):
        super().__init__(Subscription, session)

    async def get_active_by_user_and_community(
        self, user_id: uuid.UUID, community_id: uuid.UUID
    ) -> Optional[Subscription]:
        stmt = select(Subscription).where(
            and_(Subscription.user_id == user_id, Subscription.community_id == community_id, Subscription.status == "active")
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_community_subscriptions(
        self, community_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[Sequence[Subscription], int]:
        filters = [Subscription.community_id == community_id]
        items = await self.get_all(offset=offset, limit=limit, filters=filters)
        total = await self.count(filters=filters)
        return items, total

    async def count_active_by_community(self, community_id: uuid.UUID) -> int:
        return await self.count(filters=[Subscription.community_id == community_id, Subscription.status == "active"])

    async def get_level_by_id(self, level_id: uuid.UUID) -> Optional[SubscriptionLevel]:
        return await self._session.get(SubscriptionLevel, level_id)

    async def get_community_levels(self, community_id: uuid.UUID) -> Sequence[SubscriptionLevel]:
        stmt = select(SubscriptionLevel).where(SubscriptionLevel.community_id == community_id).order_by(SubscriptionLevel.price.asc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_level(self, level: SubscriptionLevel) -> SubscriptionLevel:
        self._session.add(level)
        await self._session.flush()
        await self._session.refresh(level)
        return level

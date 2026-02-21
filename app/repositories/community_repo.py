"""Репозиторий сообществ."""
from __future__ import annotations
import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Community
from app.repositories.base import BaseRepository


class CommunityRepository(BaseRepository[Community]):
    def __init__(self, session: AsyncSession):
        super().__init__(Community, session)

    async def get_by_slug(self, slug: str) -> Optional[Community]:
        stmt = select(Community).where(Community.slug == slug)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_popular(self, limit: int = 10) -> Sequence[Community]:
        stmt = (
            select(Community)
            .where(Community.status == "active")
            .order_by(Community.member_count.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def search(self, query: str, offset: int = 0, limit: int = 20) -> tuple[Sequence[Community], int]:
        search_filter = Community.name.ilike(f"%{query}%")
        items = await self.get_all(offset=offset, limit=limit, filters=[search_filter, Community.status == "active"])
        total = await self.count(filters=[search_filter, Community.status == "active"])
        return items, total

    async def increment_member_count(self, community_id: uuid.UUID, delta: int = 1) -> None:
        community = await self.get_by_id(community_id)
        if community:
            community.member_count = max(0, community.member_count + delta)
            await self._session.flush()

    async def increment_post_count(self, community_id: uuid.UUID, delta: int = 1) -> None:
        community = await self.get_by_id(community_id)
        if community:
            community.post_count = max(0, community.post_count + delta)
            await self._session.flush()

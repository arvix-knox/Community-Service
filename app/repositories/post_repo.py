"""Репозиторий постов."""
from __future__ import annotations
import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Post
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)

    async def get_community_posts(
        self, community_id: uuid.UUID, offset: int = 0, limit: int = 20,
        status_filter: Optional[str] = "published", channel_id: Optional[uuid.UUID] = None,
    ) -> tuple[Sequence[Post], int]:
        filters = [Post.community_id == community_id]
        if status_filter:
            filters.append(Post.status == status_filter)
        if channel_id:
            filters.append(Post.channel_id == channel_id)
        items = await self.get_all(offset=offset, limit=limit, filters=filters, order_by=Post.is_pinned.desc())
        total = await self.count(filters=filters)
        return items, total

    async def get_by_author(self, author_id: uuid.UUID, offset: int = 0, limit: int = 20) -> Sequence[Post]:
        return await self.get_all(offset=offset, limit=limit, filters=[Post.author_id == author_id])

    async def count_by_author(self, author_id: uuid.UUID) -> int:
        return await self.count(filters=[Post.author_id == author_id])

    async def count_by_community(self, community_id: uuid.UUID) -> int:
        return await self.count(filters=[Post.community_id == community_id])

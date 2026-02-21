"""Репозиторий каналов."""
from __future__ import annotations
import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Channel
from app.repositories.base import BaseRepository


class ChannelRepository(BaseRepository[Channel]):
    def __init__(self, session: AsyncSession):
        super().__init__(Channel, session)

    async def get_community_channels(self, community_id: uuid.UUID) -> Sequence[Channel]:
        stmt = select(Channel).where(Channel.community_id == community_id).order_by(Channel.position.asc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

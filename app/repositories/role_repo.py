"""Репозиторий ролей."""
from __future__ import annotations
import uuid
from typing import Optional, Sequence

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)

    async def get_community_roles(self, community_id: uuid.UUID) -> Sequence[Role]:
        stmt = select(Role).where(Role.community_id == community_id).order_by(Role.priority.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_default_role(self, community_id: uuid.UUID) -> Optional[Role]:
        stmt = select(Role).where(and_(Role.community_id == community_id, Role.is_default == True))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name_and_community(self, name: str, community_id: uuid.UUID) -> Optional[Role]:
        stmt = select(Role).where(and_(Role.name == name, Role.community_id == community_id))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

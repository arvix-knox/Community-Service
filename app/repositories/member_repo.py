"""Репозиторий участников."""
from __future__ import annotations
import uuid
from typing import Optional, Sequence

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models import Member, Role
from app.repositories.base import BaseRepository


class MemberRepository(BaseRepository[Member]):
    def __init__(self, session: AsyncSession):
        super().__init__(Member, session)

    async def get_by_user_and_community(
        self, user_id: uuid.UUID, community_id: uuid.UUID
    ) -> Optional[Member]:
        stmt = (
            select(Member)
            .options(selectinload(Member.roles))
            .where(and_(Member.user_id == user_id, Member.community_id == community_id))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_community_members(
        self, community_id: uuid.UUID, offset: int = 0, limit: int = 20,
        status_filter: Optional[str] = None,
    ) -> tuple[Sequence[Member], int]:
        filters = [Member.community_id == community_id]
        if status_filter:
            filters.append(Member.status == status_filter)
        items = await self.get_all(offset=offset, limit=limit, filters=filters)
        total = await self.count(filters=filters)
        return items, total

    async def assign_role(self, member_id: uuid.UUID, role: Role) -> None:
        member = await self.get_by_id(member_id)
        if member and role not in member.roles:
            member.roles.append(role)
            await self._session.flush()

    async def remove_role(self, member_id: uuid.UUID, role: Role) -> None:
        member = await self.get_by_id(member_id)
        if member and role in member.roles:
            member.roles.remove(role)
            await self._session.flush()

    async def count_active_members(self, community_id: uuid.UUID) -> int:
        return await self.count(filters=[Member.community_id == community_id, Member.status == "active"])

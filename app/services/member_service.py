"""Сервис участников."""
from __future__ import annotations
import uuid
from typing import Optional

from app.core.exceptions import ConflictException, NotFoundException, ForbiddenException
from app.core.logging import get_logger
from app.core.security import UserContext
from app.domain.models import Member
from app.events.base import EventPublisher
from app.events.event_types import EventType
from app.infrastructure.cache.cache_keys import CacheKeys
from app.infrastructure.cache.redis_client import RedisClient
from app.repositories.community_repo import CommunityRepository
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse
from app.schemas.common import PaginatedResponse

logger = get_logger(__name__)


class MemberService:
    def __init__(self, member_repo: MemberRepository, community_repo: CommunityRepository,
                 role_repo: RoleRepository, cache: RedisClient, event_publisher: EventPublisher):
        self._member_repo = member_repo
        self._community_repo = community_repo
        self._role_repo = role_repo
        self._cache = cache
        self._event_publisher = event_publisher

    async def list_members(self, community_id: uuid.UUID, page: int = 1, page_size: int = 20,
                            status_filter: Optional[str] = None) -> PaginatedResponse[MemberResponse]:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)

        offset = (page - 1) * page_size
        items, total = await self._member_repo.get_community_members(community_id, offset=offset, limit=page_size, status_filter=status_filter)
        pages = (total + page_size - 1) // page_size
        response_items = [MemberResponse.model_validate(item) for item in items]
        return PaginatedResponse[MemberResponse](items=response_items, total=total, page=page, page_size=page_size, pages=pages)

    async def join_community(self, community_id: uuid.UUID, data: MemberCreate, user: UserContext) -> MemberResponse:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)

        target_user_id = data.user_id or user.user_id
        existing = await self._member_repo.get_by_user_and_community(target_user_id, community_id)
        if existing:
            raise ConflictException("Пользователь уже является участником сообщества")

        initial_status = "pending" if community.community_type == "private" else "active"

        member = Member(community_id=community_id, user_id=target_user_id, status=initial_status, nickname=data.nickname, is_owner=False)
        member = await self._member_repo.create(member)

        default_role = await self._role_repo.get_default_role(community_id)
        if default_role:
            await self._member_repo.assign_role(member.id, default_role)

        if initial_status == "active":
            await self._community_repo.increment_member_count(community_id, 1)

        await self._cache.delete(CacheKeys.community(str(community_id)))

        await self._event_publisher.publish_event(
            EventType.MEMBER_JOINED,
            payload={"community_id": str(community_id), "user_id": str(target_user_id), "status": initial_status},
        )
        logger.info("Участник присоединился", extra={"community_id": str(community_id), "user_id": str(target_user_id), "action": "member_joined"})

        member = await self._member_repo.get_by_user_and_community(target_user_id, community_id)
        return MemberResponse.model_validate(member)

    async def update_member(self, community_id: uuid.UUID, user_id: uuid.UUID,
                             data: MemberUpdate, current_user: UserContext) -> MemberResponse:
        member = await self._member_repo.get_by_user_and_community(user_id, community_id)
        if not member:
            raise NotFoundException("Member")

        update_data = data.model_dump(exclude_unset=True, exclude={"role_ids"})
        if update_data:
            await self._member_repo.update_by_id(member.id, update_data)

        if data.role_ids is not None:
            for role in list(member.roles):
                await self._member_repo.remove_role(member.id, role)
            for role_id in data.role_ids:
                role = await self._role_repo.get_by_id(role_id)
                if role and role.community_id == community_id:
                    await self._member_repo.assign_role(member.id, role)

        member = await self._member_repo.get_by_user_and_community(user_id, community_id)
        logger.info("Участник обновлён", extra={"community_id": str(community_id), "user_id": str(user_id), "action": "member_updated"})
        return MemberResponse.model_validate(member)

    async def remove_member(self, community_id: uuid.UUID, user_id: uuid.UUID, current_user: UserContext) -> None:
        member = await self._member_repo.get_by_user_and_community(user_id, community_id)
        if not member:
            raise NotFoundException("Member")
        if member.is_owner:
            raise ForbiddenException("Нельзя удалить владельца сообщества")

        await self._member_repo.delete_by_id(member.id)
        await self._community_repo.increment_member_count(community_id, -1)
        await self._cache.delete(CacheKeys.community(str(community_id)))

        await self._event_publisher.publish_event(
            EventType.MEMBER_LEFT,
            payload={"community_id": str(community_id), "user_id": str(user_id), "removed_by": str(current_user.user_id)},
        )
        logger.info("Участник покинул сообщество", extra={"community_id": str(community_id), "user_id": str(user_id), "action": "member_left"})

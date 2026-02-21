"""Сервис сообществ."""
from __future__ import annotations
import re
import uuid
from typing import Optional

from app.core.exceptions import ConflictException, NotFoundException, ForbiddenException
from app.core.logging import get_logger
from app.core.security import UserContext
from app.core.rbac import Permission
from app.domain.models import Community, Role, Member, Channel
from app.events.base import EventPublisher
from app.events.event_types import EventType
from app.infrastructure.cache.cache_keys import CacheKeys
from app.infrastructure.cache.redis_client import RedisClient
from app.repositories.community_repo import CommunityRepository
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.channel_repo import ChannelRepository
from app.schemas.community import CommunityCreate, CommunityUpdate, CommunityResponse, CommunityListResponse
from app.schemas.common import PaginatedResponse

logger = get_logger(__name__)


class CommunityService:
    def __init__(
        self,
        community_repo: CommunityRepository,
        member_repo: MemberRepository,
        role_repo: RoleRepository,
        channel_repo: ChannelRepository,
        cache: RedisClient,
        event_publisher: EventPublisher,
    ):
        self._community_repo = community_repo
        self._member_repo = member_repo
        self._role_repo = role_repo
        self._channel_repo = channel_repo
        self._cache = cache
        self._event_publisher = event_publisher

    async def list_communities(self, page: int = 1, page_size: int = 20,
                                search: Optional[str] = None) -> PaginatedResponse[CommunityListResponse]:
        offset = (page - 1) * page_size

        if search:
            items, total = await self._community_repo.search(search, offset=offset, limit=page_size)
        else:
            cache_key = CacheKeys.community_list(page, page_size)
            cached = await self._cache.get(cache_key)
            if cached:
                return PaginatedResponse[CommunityListResponse](**cached)

            filters = [Community.status == "active"]
            items = await self._community_repo.get_all(offset=offset, limit=page_size, filters=filters)
            total = await self._community_repo.count(filters=filters)

        response_items = [CommunityListResponse.model_validate(item) for item in items]
        pages = (total + page_size - 1) // page_size

        result = PaginatedResponse[CommunityListResponse](
            items=response_items, total=total, page=page, page_size=page_size, pages=pages,
        )

        if not search:
            cache_key = CacheKeys.community_list(page, page_size)
            await self._cache.set(cache_key, result.model_dump())

        return result

    async def get_community(self, community_id: uuid.UUID) -> CommunityResponse:
        cache_key = CacheKeys.community(str(community_id))
        cached = await self._cache.get(cache_key)
        if cached:
            return CommunityResponse(**cached)

        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)

        response = CommunityResponse.model_validate(community)
        await self._cache.set(cache_key, response.model_dump())
        return response

    async def create_community(self, data: CommunityCreate, user: UserContext) -> CommunityResponse:
        slug = data.slug or self._generate_slug(data.name)

        existing = await self._community_repo.get_by_slug(slug)
        if existing:
            raise ConflictException(f"Сообщество со slug \'{slug}\' уже существует")

        community = Community(
            name=data.name, slug=slug, description=data.description,
            community_type=data.community_type, owner_id=user.user_id,
            avatar_url=data.avatar_url, banner_url=data.banner_url,
            settings=data.settings or {}, member_count=1,
        )
        community = await self._community_repo.create(community)

        default_role = Role(
            community_id=community.id, name="member", description="Default member role",
            permissions_list=["community.view", "post.create"], is_default=True, priority=0,
        )
        await self._role_repo.create(default_role)

        owner_role = Role(
            community_id=community.id, name="owner", description="Community owner",
            permissions_list=[p.value for p in Permission], is_default=False, priority=100,
        )
        await self._role_repo.create(owner_role)

        owner_member = Member(
            community_id=community.id, user_id=user.user_id, is_owner=True, status="active",
        )
        owner_member = await self._member_repo.create(owner_member)
        await self._member_repo.assign_role(owner_member.id, owner_role)

        default_channel = Channel(
            community_id=community.id, name="general", description="General discussion",
            channel_type="text", is_default=True, position=0,
        )
        await self._channel_repo.create(default_channel)

        await self._event_publisher.publish_event(
            EventType.COMMUNITY_CREATED,
            payload={"community_id": str(community.id), "owner_id": str(user.user_id), "name": community.name},
        )

        logger.info("Сообщество создано", extra={"community_id": str(community.id), "user_id": str(user.user_id), "action": "community_created"})
        return CommunityResponse.model_validate(community)

    async def update_community(self, community_id: uuid.UUID, data: CommunityUpdate, user: UserContext) -> CommunityResponse:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)

        if community.owner_id != user.user_id and not user.is_superadmin:
            member = await self._member_repo.get_by_user_and_community(user.user_id, community_id)
            if not member or not member.is_owner:
                raise ForbiddenException("Только владелец может обновлять сообщество")

        update_data = data.model_dump(exclude_unset=True)
        updated = await self._community_repo.update_by_id(community_id, update_data)
        if not updated:
            raise NotFoundException("Community", community_id)

        await self._cache.delete(CacheKeys.community(str(community_id)))

        await self._event_publisher.publish_event(
            EventType.COMMUNITY_UPDATED,
            payload={"community_id": str(community_id), "updated_fields": list(update_data.keys())},
        )
        logger.info("Сообщество обновлено", extra={"community_id": str(community_id), "action": "community_updated"})
        return CommunityResponse.model_validate(updated)

    async def delete_community(self, community_id: uuid.UUID, user: UserContext) -> None:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)

        if community.owner_id != user.user_id and not user.is_superadmin:
            raise ForbiddenException("Только владелец может удалить сообщество")

        await self._community_repo.delete_by_id(community_id)
        await self._cache.delete_pattern(CacheKeys.invalidation_pattern(str(community_id)))

        await self._event_publisher.publish_event(
            EventType.COMMUNITY_DELETED,
            payload={"community_id": str(community_id), "deleted_by": str(user.user_id)},
        )
        logger.info("Сообщество удалено", extra={"community_id": str(community_id), "action": "community_deleted"})

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = name.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        short_id = str(uuid.uuid4())[:8]
        return f"{slug}-{short_id}"

"""Сервис ролей."""
from __future__ import annotations
import uuid
from typing import List

from app.core.exceptions import ConflictException, NotFoundException
from app.core.logging import get_logger
from app.core.security import UserContext
from app.domain.models import Role
from app.infrastructure.cache.cache_keys import CacheKeys
from app.infrastructure.cache.redis_client import RedisClient
from app.repositories.community_repo import CommunityRepository
from app.repositories.role_repo import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse

logger = get_logger(__name__)


class RoleService:
    def __init__(self, role_repo: RoleRepository, community_repo: CommunityRepository, cache: RedisClient):
        self._role_repo = role_repo
        self._community_repo = community_repo
        self._cache = cache

    async def list_roles(self, community_id: uuid.UUID) -> List[RoleResponse]:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        cache_key = CacheKeys.community_roles(str(community_id))
        cached = await self._cache.get(cache_key)
        if cached:
            return [RoleResponse(**r) for r in cached]
        roles = await self._role_repo.get_community_roles(community_id)
        result = [RoleResponse.model_validate(r) for r in roles]
        await self._cache.set(cache_key, [r.model_dump() for r in result])
        return result

    async def create_role(self, community_id: uuid.UUID, data: RoleCreate, user: UserContext) -> RoleResponse:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        existing = await self._role_repo.get_by_name_and_community(data.name, community_id)
        if existing:
            raise ConflictException(f"Роль \'{data.name}\' уже существует")
        role = Role(community_id=community_id, name=data.name, description=data.description,
                    color=data.color, permissions_list=data.permissions_list or [],
                    is_default=data.is_default, priority=data.priority)
        role = await self._role_repo.create(role)
        await self._cache.delete(CacheKeys.community_roles(str(community_id)))
        logger.info("Роль создана", extra={"community_id": str(community_id), "role_id": str(role.id), "action": "role_created"})
        return RoleResponse.model_validate(role)

    async def update_role(self, community_id: uuid.UUID, role_id: uuid.UUID, data: RoleUpdate, user: UserContext) -> RoleResponse:
        role = await self._role_repo.get_by_id(role_id)
        if not role or role.community_id != community_id:
            raise NotFoundException("Role", role_id)
        update_data = data.model_dump(exclude_unset=True)
        updated = await self._role_repo.update_by_id(role_id, update_data)
        if not updated:
            raise NotFoundException("Role", role_id)
        await self._cache.delete(CacheKeys.community_roles(str(community_id)))
        return RoleResponse.model_validate(updated)

    async def delete_role(self, community_id: uuid.UUID, role_id: uuid.UUID, user: UserContext) -> None:
        role = await self._role_repo.get_by_id(role_id)
        if not role or role.community_id != community_id:
            raise NotFoundException("Role", role_id)
        await self._role_repo.delete_by_id(role_id)
        await self._cache.delete(CacheKeys.community_roles(str(community_id)))
        logger.info("Роль удалена", extra={"community_id": str(community_id), "role_id": str(role_id), "action": "role_deleted"})

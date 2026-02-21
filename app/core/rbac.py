"""RBAC — контроль доступа на основе ролей и прав."""
from __future__ import annotations
import uuid
from enum import Enum

from fastapi import Request

from app.core.security import UserContext, get_current_user
from app.core.exceptions import ForbiddenException
from app.core.logging import get_logger

logger = get_logger(__name__)


class Permission(str, Enum):
    """Системные разрешения."""
    COMMUNITY_CREATE = "community.create"
    COMMUNITY_UPDATE = "community.update"
    COMMUNITY_DELETE = "community.delete"
    COMMUNITY_VIEW = "community.view"
    MEMBER_MANAGE = "member.manage"
    MEMBER_KICK = "member.kick"
    MEMBER_BAN = "member.ban"
    ROLE_MANAGE = "role.manage"
    POST_CREATE = "post.create"
    POST_UPDATE = "post.update"
    POST_DELETE = "post.delete"
    POST_MODERATE = "post.moderate"
    CHANNEL_MANAGE = "channel.manage"
    EVENT_MANAGE = "event.manage"
    SUBSCRIPTION_MANAGE = "subscription.manage"
    ANALYTICS_VIEW = "analytics.view"
    DONATION_VIEW = "donation.view"


class RBACChecker:
    """Проверка разрешений RBAC."""

    def __init__(self, required_permissions: list[Permission], require_all: bool = True):
        self.required_permissions = required_permissions
        self.require_all = require_all

    async def __call__(self, request: Request) -> UserContext:
        user = get_current_user(request)

        if user.is_superadmin:
            return user

        await self._check_permissions(user, request)
        return user

    async def _check_permissions(self, user: UserContext, request: Request) -> None:
        community_id = request.path_params.get("community_id") or request.path_params.get("id")

        if community_id:
            member_permissions = await self._get_member_permissions(
                user.user_id, community_id, request
            )
        else:
            member_permissions = set(user.permissions)

        required = {p.value for p in self.required_permissions}

        if self.require_all:
            if not required.issubset(member_permissions):
                missing = required - member_permissions
                logger.warning(
                    "Отказ в доступе: недостаточно прав",
                    extra={
                        "user_id": str(user.user_id),
                        "missing_permissions": list(missing),
                        "action": "rbac_denied",
                    },
                )
                raise ForbiddenException(f"Отсутствуют разрешения: {', '.join(missing)}")
        else:
            if not required.intersection(member_permissions):
                raise ForbiddenException("Недостаточно прав для данного действия")

    async def _get_member_permissions(
        self, user_id: uuid.UUID, community_id: str, request: Request
    ) -> set[str]:
        container = request.app.state.container
        try:
            community_uuid = uuid.UUID(community_id)
        except ValueError:
            return set()

        async with container.db_session() as session:
            member_repo = container.member_repo(session)
            member = await member_repo.get_by_user_and_community(user_id, community_uuid)

            if not member:
                return {Permission.COMMUNITY_VIEW.value}

            permissions: set[str] = set()
            if member.roles:
                for role in member.roles:
                    if role.permissions_list:
                        for perm in role.permissions_list:
                            permissions.add(perm)

            if member.is_owner:
                permissions = {p.value for p in Permission}

            return permissions


def require_permissions(*permissions: Permission, require_all: bool = True):
    """Фабрика dependency для проверки разрешений."""
    return RBACChecker(list(permissions), require_all=require_all)


def require_auth():
    """Dependency для обязательной аутентификации без проверки прав."""
    async def _check(request: Request) -> UserContext:
        return get_current_user(request)
    return _check

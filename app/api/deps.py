"""Зависимости для API endpoints."""
from __future__ import annotations
from typing import Optional

from fastapi import Query, Request

from app.core.config import settings
from app.core.security import UserContext, get_current_user, get_optional_user
from app.infrastructure.container import Container
from app.schemas.common import PaginationParams


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_pagination(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=min(page_size, settings.MAX_PAGE_SIZE))


async def get_current_user_dep(request: Request) -> UserContext:
    return get_current_user(request)


async def get_optional_user_dep(request: Request) -> Optional[UserContext]:
    return get_optional_user(request)

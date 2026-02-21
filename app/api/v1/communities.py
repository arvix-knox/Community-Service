"""Endpoints для Communities."""
from __future__ import annotations
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_container, get_current_user_dep, get_pagination
from app.core.security import UserContext
from app.infrastructure.container import Container
from app.schemas.common import PaginatedResponse, MessageResponse, PaginationParams
from app.schemas.community import CommunityCreate, CommunityUpdate, CommunityResponse, CommunityListResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CommunityListResponse])
async def list_communities(
    pagination: PaginationParams = Depends(get_pagination),
    search: Optional[str] = Query(None, max_length=255),
    container: Container = Depends(get_container),
):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.list_communities(page=pagination.page, page_size=pagination.page_size, search=search)


@router.get("/{id}", response_model=CommunityResponse)
async def get_community(id: uuid.UUID, container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.get_community(id)


@router.post("", response_model=CommunityResponse, status_code=201)
async def create_community(data: CommunityCreate, user: UserContext = Depends(get_current_user_dep),
                            container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.create_community(data, user)


@router.put("/{id}", response_model=CommunityResponse)
async def update_community(id: uuid.UUID, data: CommunityUpdate, user: UserContext = Depends(get_current_user_dep),
                            container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.update_community(id, data, user)


@router.delete("/{id}", response_model=MessageResponse)
async def delete_community(id: uuid.UUID, user: UserContext = Depends(get_current_user_dep),
                            container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        await service.delete_community(id, user)
        return MessageResponse(message="Сообщество удалено")


def _build_service(container, session):
    from app.services.community_service import CommunityService
    return CommunityService(
        community_repo=container.community_repo(session), member_repo=container.member_repo(session),
        role_repo=container.role_repo(session), channel_repo=container.channel_repo(session),
        cache=container.redis, event_publisher=container.event_publisher,
    )

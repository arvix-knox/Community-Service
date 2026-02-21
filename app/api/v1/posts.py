"""Endpoints для Posts."""
from __future__ import annotations
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_container, get_current_user_dep, get_pagination
from app.core.security import UserContext
from app.infrastructure.container import Container
from app.schemas.common import PaginatedResponse, MessageResponse, PaginationParams
from app.schemas.post import PostCreate, PostUpdate, PostResponse

router = APIRouter()


@router.get("/communities/{id}/posts", response_model=PaginatedResponse[PostResponse])
async def list_posts(id: uuid.UUID, pagination: PaginationParams = Depends(get_pagination),
                      channel_id: Optional[uuid.UUID] = Query(None), container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.list_posts(community_id=id, page=pagination.page, page_size=pagination.page_size, channel_id=channel_id)


@router.get("/posts/{id}", response_model=PostResponse)
async def get_post(id: uuid.UUID, container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.get_post(id)


@router.post("/communities/{id}/posts", response_model=PostResponse, status_code=201)
async def create_post(id: uuid.UUID, data: PostCreate, user: UserContext = Depends(get_current_user_dep),
                       container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.create_post(id, data, user)


@router.put("/posts/{id}", response_model=PostResponse)
async def update_post(id: uuid.UUID, data: PostUpdate, user: UserContext = Depends(get_current_user_dep),
                       container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.update_post(id, data, user)


@router.delete("/posts/{id}", response_model=MessageResponse)
async def delete_post(id: uuid.UUID, user: UserContext = Depends(get_current_user_dep),
                       container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        await service.delete_post(id, user)
        return MessageResponse(message="Пост удалён")


def _build_service(container, session):
    from app.services.post_service import PostService
    return PostService(post_repo=container.post_repo(session), community_repo=container.community_repo(session),
                       cache=container.redis, event_publisher=container.event_publisher)

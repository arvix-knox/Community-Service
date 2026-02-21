"""Endpoints для Members."""
from __future__ import annotations
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_container, get_current_user_dep, get_pagination
from app.core.security import UserContext
from app.infrastructure.container import Container
from app.schemas.common import PaginatedResponse, MessageResponse, PaginationParams
from app.schemas.member import MemberCreate, MemberUpdate, MemberResponse

router = APIRouter()


@router.get("/communities/{id}/members", response_model=PaginatedResponse[MemberResponse])
async def list_members(id: uuid.UUID, pagination: PaginationParams = Depends(get_pagination),
                        status: Optional[str] = Query(None), container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.list_members(community_id=id, page=pagination.page, page_size=pagination.page_size, status_filter=status)


@router.post("/communities/{id}/members", response_model=MemberResponse, status_code=201)
async def join_community(id: uuid.UUID, data: MemberCreate, user: UserContext = Depends(get_current_user_dep),
                          container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.join_community(id, data, user)


@router.put("/communities/{id}/members/{user_id}", response_model=MemberResponse)
async def update_member(id: uuid.UUID, user_id: uuid.UUID, data: MemberUpdate,
                         user: UserContext = Depends(get_current_user_dep), container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.update_member(id, user_id, data, user)


@router.delete("/communities/{id}/members/{user_id}", response_model=MessageResponse)
async def remove_member(id: uuid.UUID, user_id: uuid.UUID, user: UserContext = Depends(get_current_user_dep),
                         container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        await service.remove_member(id, user_id, user)
        return MessageResponse(message="Участник удалён")


def _build_service(container, session):
    from app.services.member_service import MemberService
    return MemberService(member_repo=container.member_repo(session), community_repo=container.community_repo(session),
                         role_repo=container.role_repo(session), cache=container.redis, event_publisher=container.event_publisher)

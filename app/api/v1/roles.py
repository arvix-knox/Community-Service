"""Endpoints для Roles."""
from __future__ import annotations
import uuid
from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_container, get_current_user_dep
from app.core.security import UserContext
from app.infrastructure.container import Container
from app.schemas.common import MessageResponse
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse

router = APIRouter()


@router.get("/communities/{id}/roles", response_model=List[RoleResponse])
async def list_roles(id: uuid.UUID, container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.list_roles(id)


@router.post("/communities/{id}/roles", response_model=RoleResponse, status_code=201)
async def create_role(id: uuid.UUID, data: RoleCreate, user: UserContext = Depends(get_current_user_dep),
                       container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.create_role(id, data, user)


@router.put("/communities/{id}/roles/{role_id}", response_model=RoleResponse)
async def update_role(id: uuid.UUID, role_id: uuid.UUID, data: RoleUpdate,
                       user: UserContext = Depends(get_current_user_dep), container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.update_role(id, role_id, data, user)


@router.delete("/communities/{id}/roles/{role_id}", response_model=MessageResponse)
async def delete_role(id: uuid.UUID, role_id: uuid.UUID, user: UserContext = Depends(get_current_user_dep),
                       container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        await service.delete_role(id, role_id, user)
        return MessageResponse(message="Роль удалена")


def _build_service(container, session):
    from app.services.role_service import RoleService
    return RoleService(role_repo=container.role_repo(session), community_repo=container.community_repo(session), cache=container.redis)

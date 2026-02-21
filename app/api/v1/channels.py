"""Endpoints для Channels."""
from __future__ import annotations
import uuid
from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_container, get_current_user_dep
from app.core.security import UserContext
from app.infrastructure.container import Container
from app.schemas.common import MessageResponse
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse

router = APIRouter()


@router.get("/communities/{id}/channels", response_model=List[ChannelResponse])
async def list_channels(id: uuid.UUID, container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.list_channels(id)


@router.post("/communities/{id}/channels", response_model=ChannelResponse, status_code=201)
async def create_channel(id: uuid.UUID, data: ChannelCreate, user: UserContext = Depends(get_current_user_dep),
                          container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.create_channel(id, data, user)


@router.put("/channels/{id}", response_model=ChannelResponse)
async def update_channel(id: uuid.UUID, data: ChannelUpdate, user: UserContext = Depends(get_current_user_dep),
                          container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.update_channel(id, data, user)


@router.delete("/channels/{id}", response_model=MessageResponse)
async def delete_channel(id: uuid.UUID, user: UserContext = Depends(get_current_user_dep),
                          container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        await service.delete_channel(id, user)
        return MessageResponse(message="Канал удалён")


def _build_service(container, session):
    from app.services.channel_service import ChannelService
    return ChannelService(channel_repo=container.channel_repo(session), community_repo=container.community_repo(session))

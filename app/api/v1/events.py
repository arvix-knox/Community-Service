"""Endpoints для Events."""
from __future__ import annotations
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_container, get_current_user_dep, get_pagination
from app.core.security import UserContext
from app.infrastructure.container import Container
from app.schemas.common import PaginatedResponse, MessageResponse, PaginationParams
from app.schemas.event import EventCreate, EventUpdate, EventResponse

router = APIRouter()


@router.get("/communities/{id}/events", response_model=PaginatedResponse[EventResponse])
async def list_events(id: uuid.UUID, pagination: PaginationParams = Depends(get_pagination),
                       status: Optional[str] = Query(None), container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.list_events(community_id=id, page=pagination.page, page_size=pagination.page_size, status_filter=status)


@router.get("/events/{id}", response_model=EventResponse)
async def get_event(id: uuid.UUID, container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.get_event(id)


@router.post("/communities/{id}/events", response_model=EventResponse, status_code=201)
async def create_event(id: uuid.UUID, data: EventCreate, user: UserContext = Depends(get_current_user_dep),
                        container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.create_event(id, data, user)


@router.put("/events/{id}", response_model=EventResponse)
async def update_event(id: uuid.UUID, data: EventUpdate, user: UserContext = Depends(get_current_user_dep),
                        container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.update_event(id, data, user)


@router.delete("/events/{id}", response_model=MessageResponse)
async def delete_event(id: uuid.UUID, user: UserContext = Depends(get_current_user_dep),
                        container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        await service.delete_event(id, user)
        return MessageResponse(message="Мероприятие удалено")


def _build_service(container, session):
    from app.services.event_service import EventService
    return EventService(event_repo=container.event_repo(session), community_repo=container.community_repo(session),
                        event_publisher=container.event_publisher)

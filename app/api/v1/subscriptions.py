"""Endpoints для Subscriptions."""
from __future__ import annotations
import uuid
from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_container, get_current_user_dep
from app.core.security import UserContext
from app.infrastructure.container import Container
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionLevelResponse

router = APIRouter()


@router.get("/communities/{id}/subscriptions", response_model=List[SubscriptionLevelResponse])
async def get_subscription_levels(id: uuid.UUID, container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.get_levels(id)


@router.post("/communities/{id}/subscriptions", response_model=SubscriptionResponse, status_code=201)
async def subscribe(id: uuid.UUID, data: SubscriptionCreate, user: UserContext = Depends(get_current_user_dep),
                     container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.subscribe(id, data, user)


def _build_service(container, session):
    from app.services.subscription_service import SubscriptionService
    return SubscriptionService(subscription_repo=container.subscription_repo(session),
                                community_repo=container.community_repo(session), event_publisher=container.event_publisher)

"""Endpoints для Analytics."""
from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_container, get_current_user_dep
from app.core.security import UserContext
from app.infrastructure.container import Container
from app.schemas.analytics import CommunityAnalytics, PostAnalytics, MemberAnalytics

router = APIRouter()


@router.get("/communities/{id}/analytics", response_model=CommunityAnalytics)
async def get_community_analytics(id: uuid.UUID, user: UserContext = Depends(get_current_user_dep),
                                   container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.get_community_analytics(id)


@router.get("/posts/{id}/analytics", response_model=PostAnalytics)
async def get_post_analytics(id: uuid.UUID, user: UserContext = Depends(get_current_user_dep),
                              container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.get_post_analytics(id)


@router.get("/members/{id}/analytics", response_model=MemberAnalytics)
async def get_member_analytics(id: uuid.UUID, user: UserContext = Depends(get_current_user_dep),
                                container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.get_member_analytics(id)


def _build_service(container, session):
    from app.services.analytics_service import AnalyticsService
    return AnalyticsService(
        community_repo=container.community_repo(session), member_repo=container.member_repo(session),
        post_repo=container.post_repo(session), event_repo=container.event_repo(session),
        donation_repo=container.donation_repo(session), subscription_repo=container.subscription_repo(session),
        cache=container.redis,
    )

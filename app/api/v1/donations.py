"""Endpoints для Donations."""
from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends

from app.api.deps import get_container, get_current_user_dep, get_pagination
from app.core.security import UserContext
from app.infrastructure.container import Container
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.donation import DonationCreate, DonationResponse

router = APIRouter()


@router.get("/communities/{id}/donations", response_model=PaginatedResponse[DonationResponse])
async def list_donations(id: uuid.UUID, pagination: PaginationParams = Depends(get_pagination),
                          container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.list_donations(community_id=id, page=pagination.page, page_size=pagination.page_size)


@router.post("/communities/{id}/donations", response_model=DonationResponse, status_code=201)
async def create_donation(id: uuid.UUID, data: DonationCreate, user: UserContext = Depends(get_current_user_dep),
                           container: Container = Depends(get_container)):
    async with container.db_session() as session:
        service = _build_service(container, session)
        return await service.create_donation(id, data, user)


def _build_service(container, session):
    from app.services.donation_service import DonationService
    return DonationService(donation_repo=container.donation_repo(session), community_repo=container.community_repo(session),
                           cache=container.redis, event_publisher=container.event_publisher)

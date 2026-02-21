"""Сервис донатов."""
from __future__ import annotations
import uuid

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.core.security import UserContext
from app.domain.models import Donation
from app.events.base import EventPublisher
from app.events.event_types import EventType
from app.infrastructure.cache.cache_keys import CacheKeys
from app.infrastructure.cache.redis_client import RedisClient
from app.repositories.community_repo import CommunityRepository
from app.repositories.donation_repo import DonationRepository
from app.schemas.donation import DonationCreate, DonationResponse
from app.schemas.common import PaginatedResponse

logger = get_logger(__name__)


class DonationService:
    def __init__(self, donation_repo: DonationRepository, community_repo: CommunityRepository,
                 cache: RedisClient, event_publisher: EventPublisher):
        self._donation_repo = donation_repo
        self._community_repo = community_repo
        self._cache = cache
        self._event_publisher = event_publisher

    async def list_donations(self, community_id: uuid.UUID, page: int = 1, page_size: int = 20) -> PaginatedResponse[DonationResponse]:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        offset = (page - 1) * page_size
        items, total = await self._donation_repo.get_community_donations(community_id, offset=offset, limit=page_size)
        pages = (total + page_size - 1) // page_size
        response_items = [DonationResponse.model_validate(item) for item in items]
        return PaginatedResponse[DonationResponse](items=response_items, total=total, page=page, page_size=page_size, pages=pages)

    async def create_donation(self, community_id: uuid.UUID, data: DonationCreate, user: UserContext) -> DonationResponse:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        transaction_id = str(uuid.uuid4())
        donation = Donation(community_id=community_id, donor_id=user.user_id, amount=data.amount,
                            currency=data.currency, message=data.message, status="completed",
                            transaction_id=transaction_id, is_anonymous=data.is_anonymous)
        donation = await self._donation_repo.create(donation)
        await self._cache.delete(CacheKeys.top_donors(str(community_id)))
        await self._event_publisher.publish_event(EventType.DONATION_RECEIVED,
            payload={"donation_id": str(donation.id), "community_id": str(community_id),
                     "donor_id": str(user.user_id), "amount": str(donation.amount), "currency": donation.currency})
        logger.info("Донат получен", extra={"donation_id": str(donation.id), "amount": str(donation.amount), "action": "donation_received"})
        return DonationResponse.model_validate(donation)

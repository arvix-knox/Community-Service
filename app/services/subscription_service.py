"""Сервис подписок."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone, timedelta
from typing import List

from app.core.exceptions import ConflictException, NotFoundException
from app.core.logging import get_logger
from app.core.security import UserContext
from app.domain.models import Subscription, SubscriptionLevel
from app.events.base import EventPublisher
from app.events.event_types import EventType
from app.repositories.community_repo import CommunityRepository
from app.repositories.subscription_repo import SubscriptionRepository
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionLevelCreate, SubscriptionLevelResponse

logger = get_logger(__name__)


class SubscriptionService:
    def __init__(self, subscription_repo: SubscriptionRepository, community_repo: CommunityRepository, event_publisher: EventPublisher):
        self._subscription_repo = subscription_repo
        self._community_repo = community_repo
        self._event_publisher = event_publisher

    async def get_levels(self, community_id: uuid.UUID) -> List[SubscriptionLevelResponse]:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        levels = await self._subscription_repo.get_community_levels(community_id)
        return [SubscriptionLevelResponse.model_validate(l) for l in levels]

    async def create_level(self, community_id: uuid.UUID, data: SubscriptionLevelCreate, user: UserContext) -> SubscriptionLevelResponse:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        level = SubscriptionLevel(community_id=community_id, name=data.name, description=data.description,
                                   price=data.price, currency=data.currency, duration_days=data.duration_days,
                                   features=data.features or {}, max_subscribers=data.max_subscribers)
        level = await self._subscription_repo.create_level(level)
        return SubscriptionLevelResponse.model_validate(level)

    async def subscribe(self, community_id: uuid.UUID, data: SubscriptionCreate, user: UserContext) -> SubscriptionResponse:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        level = await self._subscription_repo.get_level_by_id(data.level_id)
        if not level or level.community_id != community_id:
            raise NotFoundException("Subscription Level", data.level_id)
        existing = await self._subscription_repo.get_active_by_user_and_community(user.user_id, community_id)
        if existing:
            raise ConflictException("Активная подписка уже существует")
        now = datetime.now(timezone.utc)
        subscription = Subscription(level_id=level.id, user_id=user.user_id, community_id=community_id,
                                     status="active", starts_at=now, expires_at=now + timedelta(days=level.duration_days),
                                     auto_renew=data.auto_renew)
        subscription = await self._subscription_repo.create(subscription)
        await self._event_publisher.publish_event(EventType.SUBSCRIPTION_STARTED,
            payload={"subscription_id": str(subscription.id), "community_id": str(community_id),
                     "user_id": str(user.user_id), "level": level.name})
        logger.info("Подписка оформлена", extra={"subscription_id": str(subscription.id), "action": "subscription_started"})
        return SubscriptionResponse.model_validate(subscription)

"""Сервис аналитики."""
from __future__ import annotations
import uuid
from decimal import Decimal

from app.core.config import settings
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.infrastructure.cache.cache_keys import CacheKeys
from app.infrastructure.cache.redis_client import RedisClient
from app.repositories.community_repo import CommunityRepository
from app.repositories.donation_repo import DonationRepository
from app.repositories.member_repo import MemberRepository
from app.repositories.post_repo import PostRepository
from app.repositories.event_repo import EventRepository
from app.repositories.subscription_repo import SubscriptionRepository
from app.schemas.analytics import CommunityAnalytics, PostAnalytics, MemberAnalytics, DonorInfo

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self, community_repo: CommunityRepository, member_repo: MemberRepository,
                 post_repo: PostRepository, event_repo: EventRepository,
                 donation_repo: DonationRepository, subscription_repo: SubscriptionRepository,
                 cache: RedisClient):
        self._community_repo = community_repo
        self._member_repo = member_repo
        self._post_repo = post_repo
        self._event_repo = event_repo
        self._donation_repo = donation_repo
        self._subscription_repo = subscription_repo
        self._cache = cache

    async def get_community_analytics(self, community_id: uuid.UUID) -> CommunityAnalytics:
        cache_key = CacheKeys.community_analytics(str(community_id))
        cached = await self._cache.get(cache_key)
        if cached:
            return CommunityAnalytics(**cached)
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        total_members = community.member_count
        active_members = await self._member_repo.count_active_members(community_id)
        total_posts = await self._post_repo.count_by_community(community_id)
        total_events = await self._event_repo.count_by_community(community_id)
        total_donations = await self._donation_repo.get_total_donations(community_id)
        total_subscriptions = await self._subscription_repo.count_active_by_community(community_id)
        top_donors_raw = await self._donation_repo.get_top_donors(community_id, limit=10)
        top_donors = [DonorInfo(**d) for d in top_donors_raw]
        engagement_rate = round(active_members / total_members * 100, 2) if total_members > 0 else 0.0
        result = CommunityAnalytics(
            total_members=total_members, active_members=active_members, total_posts=total_posts,
            total_events=total_events, total_donations=total_donations, total_subscriptions=total_subscriptions,
            member_growth_7d=0, post_growth_7d=0, top_donors=top_donors, engagement_rate=engagement_rate,
        )
        await self._cache.set(cache_key, result.model_dump(), ttl=settings.CACHE_ANALYTICS_TTL)
        return result

    async def get_post_analytics(self, post_id: uuid.UUID) -> PostAnalytics:
        cache_key = CacheKeys.post_analytics(str(post_id))
        cached = await self._cache.get(cache_key)
        if cached:
            return PostAnalytics(**cached)
        post = await self._post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException("Post", post_id)
        engagement_rate = round((post.like_count + post.comment_count) / post.view_count * 100, 2) if post.view_count > 0 else 0.0
        result = PostAnalytics(view_count=post.view_count, like_count=post.like_count,
                                comment_count=post.comment_count, engagement_rate=engagement_rate, unique_viewers=post.view_count)
        await self._cache.set(cache_key, result.model_dump(), ttl=settings.CACHE_ANALYTICS_TTL)
        return result

    async def get_member_analytics(self, member_user_id: uuid.UUID) -> MemberAnalytics:
        cache_key = CacheKeys.member_analytics(str(member_user_id))
        cached = await self._cache.get(cache_key)
        if cached:
            return MemberAnalytics(**cached)
        total_posts = await self._post_repo.count_by_author(member_user_id)
        result = MemberAnalytics(communities_count=0, total_posts=total_posts,
                                  total_donations=Decimal("0"), joined_since=None, activity_score=0.0)
        await self._cache.set(cache_key, result.model_dump(), ttl=settings.CACHE_ANALYTICS_TTL)
        return result

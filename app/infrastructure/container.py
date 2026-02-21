"""DI-контейнер — центр зависимостей приложения."""
from __future__ import annotations
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import async_session_factory, engine
from app.events.base import EventPublisher
from app.events.publisher import create_event_publisher
from app.infrastructure.cache.redis_client import RedisClient
from app.infrastructure.media.s3_client import S3Client
from app.repositories.community_repo import CommunityRepository
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.repositories.post_repo import PostRepository
from app.repositories.channel_repo import ChannelRepository
from app.repositories.event_repo import EventRepository
from app.repositories.subscription_repo import SubscriptionRepository
from app.repositories.donation_repo import DonationRepository

logger = get_logger(__name__)


class Container:
    def __init__(self):
        self._redis: RedisClient = RedisClient()
        self._event_publisher: EventPublisher = create_event_publisher()
        self._s3_client: S3Client = S3Client()

    async def init_resources(self) -> None:
        await self._redis.connect()
        await self._event_publisher.connect()
        await self._s3_client.connect()
        logger.info("Все ресурсы контейнера инициализированы")

    async def shutdown_resources(self) -> None:
        await self._redis.disconnect()
        await self._event_publisher.disconnect()
        await self._s3_client.disconnect()
        await engine.dispose()
        logger.info("Все ресурсы контейнера освобождены")

    @property
    def redis(self) -> RedisClient:
        return self._redis

    @property
    def event_publisher(self) -> EventPublisher:
        return self._event_publisher

    @property
    def s3_client(self) -> S3Client:
        return self._s3_client

    @asynccontextmanager
    async def db_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def community_repo(self, session: AsyncSession) -> CommunityRepository:
        return CommunityRepository(session)

    def member_repo(self, session: AsyncSession) -> MemberRepository:
        return MemberRepository(session)

    def role_repo(self, session: AsyncSession) -> RoleRepository:
        return RoleRepository(session)

    def post_repo(self, session: AsyncSession) -> PostRepository:
        return PostRepository(session)

    def channel_repo(self, session: AsyncSession) -> ChannelRepository:
        return ChannelRepository(session)

    def event_repo(self, session: AsyncSession) -> EventRepository:
        return EventRepository(session)

    def subscription_repo(self, session: AsyncSession) -> SubscriptionRepository:
        return SubscriptionRepository(session)

    def donation_repo(self, session: AsyncSession) -> DonationRepository:
        return DonationRepository(session)

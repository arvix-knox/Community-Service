"""Сервис постов."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core.exceptions import NotFoundException, ForbiddenException
from app.core.logging import get_logger
from app.core.security import UserContext
from app.domain.models import Post
from app.events.base import EventPublisher
from app.events.event_types import EventType
from app.infrastructure.cache.cache_keys import CacheKeys
from app.infrastructure.cache.redis_client import RedisClient
from app.repositories.community_repo import CommunityRepository
from app.repositories.post_repo import PostRepository
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.schemas.common import PaginatedResponse

logger = get_logger(__name__)


class PostService:
    def __init__(self, post_repo: PostRepository, community_repo: CommunityRepository,
                 cache: RedisClient, event_publisher: EventPublisher):
        self._post_repo = post_repo
        self._community_repo = community_repo
        self._cache = cache
        self._event_publisher = event_publisher

    async def list_posts(self, community_id: uuid.UUID, page: int = 1, page_size: int = 20,
                          channel_id: Optional[uuid.UUID] = None) -> PaginatedResponse[PostResponse]:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        offset = (page - 1) * page_size
        items, total = await self._post_repo.get_community_posts(community_id, offset=offset, limit=page_size, channel_id=channel_id)
        pages = (total + page_size - 1) // page_size
        response_items = [PostResponse.model_validate(item) for item in items]
        return PaginatedResponse[PostResponse](items=response_items, total=total, page=page, page_size=page_size, pages=pages)

    async def get_post(self, post_id: uuid.UUID) -> PostResponse:
        post = await self._post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException("Post", post_id)
        return PostResponse.model_validate(post)

    async def create_post(self, community_id: uuid.UUID, data: PostCreate, user: UserContext) -> PostResponse:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        published_at = datetime.now(timezone.utc) if data.status == "published" else None
        post = Post(community_id=community_id, channel_id=data.channel_id, author_id=user.user_id,
                    title=data.title, content=data.content, status=data.status, is_pinned=data.is_pinned,
                    media_urls=data.media_urls or [], published_at=published_at)
        post = await self._post_repo.create(post)
        if data.status == "published":
            await self._community_repo.increment_post_count(community_id, 1)
        await self._cache.delete(CacheKeys.community(str(community_id)))
        await self._event_publisher.publish_event(EventType.POST_CREATED,
            payload={"post_id": str(post.id), "community_id": str(community_id), "author_id": str(user.user_id)})
        logger.info("Пост создан", extra={"post_id": str(post.id), "action": "post_created"})
        return PostResponse.model_validate(post)

    async def update_post(self, post_id: uuid.UUID, data: PostUpdate, user: UserContext) -> PostResponse:
        post = await self._post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException("Post", post_id)
        if post.author_id != user.user_id and not user.is_superadmin:
            raise ForbiddenException("Только автор может редактировать пост")
        update_data = data.model_dump(exclude_unset=True)
        updated = await self._post_repo.update_by_id(post_id, update_data)
        if not updated:
            raise NotFoundException("Post", post_id)
        await self._event_publisher.publish_event(EventType.POST_UPDATED,
            payload={"post_id": str(post_id), "updated_fields": list(update_data.keys())})
        logger.info("Пост обновлён", extra={"post_id": str(post_id), "action": "post_updated"})
        return PostResponse.model_validate(updated)

    async def delete_post(self, post_id: uuid.UUID, user: UserContext) -> None:
        post = await self._post_repo.get_by_id(post_id)
        if not post:
            raise NotFoundException("Post", post_id)
        if post.author_id != user.user_id and not user.is_superadmin:
            raise ForbiddenException("Только автор может удалить пост")
        community_id = post.community_id
        await self._post_repo.delete_by_id(post_id)
        await self._community_repo.increment_post_count(community_id, -1)
        await self._event_publisher.publish_event(EventType.POST_DELETED,
            payload={"post_id": str(post_id), "community_id": str(community_id)})
        logger.info("Пост удалён", extra={"post_id": str(post_id), "action": "post_deleted"})

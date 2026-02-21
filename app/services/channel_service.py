"""Сервис каналов."""
from __future__ import annotations
import uuid
from typing import List

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.core.security import UserContext
from app.domain.models import Channel
from app.repositories.channel_repo import ChannelRepository
from app.repositories.community_repo import CommunityRepository
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse

logger = get_logger(__name__)


class ChannelService:
    def __init__(self, channel_repo: ChannelRepository, community_repo: CommunityRepository):
        self._channel_repo = channel_repo
        self._community_repo = community_repo

    async def list_channels(self, community_id: uuid.UUID) -> List[ChannelResponse]:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        channels = await self._channel_repo.get_community_channels(community_id)
        return [ChannelResponse.model_validate(ch) for ch in channels]

    async def create_channel(self, community_id: uuid.UUID, data: ChannelCreate, user: UserContext) -> ChannelResponse:
        community = await self._community_repo.get_by_id(community_id)
        if not community:
            raise NotFoundException("Community", community_id)
        channel = Channel(community_id=community_id, name=data.name, description=data.description,
                          channel_type=data.channel_type, is_default=data.is_default,
                          position=data.position, settings=data.settings or {})
        channel = await self._channel_repo.create(channel)
        logger.info("Канал создан", extra={"channel_id": str(channel.id), "action": "channel_created"})
        return ChannelResponse.model_validate(channel)

    async def update_channel(self, channel_id: uuid.UUID, data: ChannelUpdate, user: UserContext) -> ChannelResponse:
        channel = await self._channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundException("Channel", channel_id)
        update_data = data.model_dump(exclude_unset=True)
        updated = await self._channel_repo.update_by_id(channel_id, update_data)
        if not updated:
            raise NotFoundException("Channel", channel_id)
        return ChannelResponse.model_validate(updated)

    async def delete_channel(self, channel_id: uuid.UUID, user: UserContext) -> None:
        channel = await self._channel_repo.get_by_id(channel_id)
        if not channel:
            raise NotFoundException("Channel", channel_id)
        await self._channel_repo.delete_by_id(channel_id)
        logger.info("Канал удалён", extra={"channel_id": str(channel_id), "action": "channel_deleted"})

"""Redis-клиент для кэширования."""
from __future__ import annotations
import json
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisClient:
    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        try:
            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            await self._redis.ping()
            logger.info("Redis подключён")
        except Exception as e:
            logger.error(f"Не удалось подключиться к Redis: {e}")
            self._redis = None

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.close()
            logger.info("Redis отключён")

    @property
    def is_connected(self) -> bool:
        return self._redis is not None

    async def get(self, key: str) -> Optional[Any]:
        if not self._redis:
            return None
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis GET ошибка: {e}", extra={"key": key})
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if not self._redis:
            return
        try:
            serialized = json.dumps(value, default=str)
            await self._redis.set(key, serialized, ex=ttl or settings.CACHE_DEFAULT_TTL)
        except Exception as e:
            logger.warning(f"Redis SET ошибка: {e}", extra={"key": key})

    async def delete(self, key: str) -> None:
        if not self._redis:
            return
        try:
            await self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis DELETE ошибка: {e}", extra={"key": key})

    async def delete_pattern(self, pattern: str) -> None:
        if not self._redis:
            return
        try:
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            logger.warning(f"Redis DELETE_PATTERN ошибка: {e}", extra={"pattern": pattern})

    async def incr(self, key: str) -> Optional[int]:
        if not self._redis:
            return None
        try:
            return await self._redis.incr(key)
        except Exception as e:
            logger.warning(f"Redis INCR ошибка: {e}", extra={"key": key})
            return None

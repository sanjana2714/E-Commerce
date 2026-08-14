import json
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger

class RedisClient:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        try:
            self.redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=3.0,
            )
            await self.redis.ping()
            logger.info("Connected to Redis server successfully.")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Falling back to non-cached execution.")
            self.redis = None

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[str]:
        if not self.redis:
            return None
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.warning(f"Redis GET failed for key {key}: {e}")
            return None

    async def set(self, key: str, value: str, ttl_seconds: int = 300):
        if not self.redis:
            return
        try:
            await self.redis.set(key, value, ex=ttl_seconds)
        except Exception as e:
            logger.warning(f"Redis SET failed for key {key}: {e}")

    async def delete(self, key: str):
        if not self.redis:
            return
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis DELETE failed for key {key}: {e}")

redis_client = RedisClient()

class CacheService:
    def __init__(self, client: RedisClient = redis_client):
        self.client = client

    async def get_json(self, key: str) -> Optional[Any]:
        val = await self.client.get(key)
        if val:
            try:
                return json.loads(val)
            except Exception:
                return None
        return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 300):
        try:
            serialized = json.dumps(value)
            await self.client.set(key, serialized, ttl_seconds)
        except Exception as e:
            logger.warning(f"Failed to serialize cache value for key {key}: {e}")

    async def invalidate(self, key: str):
        await self.client.delete(key)

cache_service = CacheService()

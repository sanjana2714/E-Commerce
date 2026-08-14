import time
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.exceptions import DomainException

class RateLimitExceededError(DomainException):
    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(message=message, code="RATE_LIMIT_EXCEEDED", status_code=429)

class RedisRateLimiter:
    """
    Sliding window rate limiter backed by Redis sorted sets (ZSET).
    Key format: rate_limit:{identifier}
    """
    def __init__(self, redis_client: Optional[aioredis.Redis] = None, window_seconds: int = 60, max_requests: int = 100):
        self.redis = redis_client
        self.window_seconds = window_seconds
        self.max_requests = max_requests

    async def is_rate_limited(self, identifier: str, limit: Optional[int] = None) -> bool:
        if not self.redis:
            return False  # Graceful fallback if Redis unavailable
        
        max_reqs = limit or self.max_requests
        now = time.time()
        clear_before = now - self.window_seconds
        key = f"rate_limit:{identifier}"

        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                pipe.zremrangebyscore(key, 0, clear_before)
                pipe.zcard(key)
                pipe.zadd(key, {str(now): now})
                pipe.expire(key, self.window_seconds + 1)
                results = await pipe.execute()
                
            current_count = results[1]
            return current_count >= max_reqs
        except Exception:
            # Fallback gracefully during Redis disruption
            return False

rate_limiter = RedisRateLimiter()

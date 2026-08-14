# Cache-Aside & Rate Limiting Strategy

## Overview

The platform uses **Redis 7** for in-memory caching and API rate limiting.

---

## 1. Cache-Aside Pattern
1. API receives a search or product request.
2. API queries Redis using cache key format `search:q=...`.
3. If **Cache Hit**: Returns serialized JSON data immediately.
4. If **Cache Miss**: Queries OpenSearch / PostgreSQL, writes result to Redis with TTL (e.g. 300s), and returns response.
5. On **Product Update / Delete**: Invalidation key is purged from Redis immediately.

---

## 2. Sliding Window Rate Limiting Algorithm
We implement a **sliding-window log rate limiter** using Redis Sorted Sets (`ZSET`).
- Key: `rate_limit:{client_ip}`
- Score & Value: Current unix timestamp in seconds (`time.time()`)
- Logic:
  1. Remove timestamps older than `now - 60s` (`ZREMRANGEBYSCORE`).
  2. Count remaining records (`ZCARD`).
  3. If count >= 100 limit, return HTTP `429 Too Many Requests`.
  4. Otherwise, add current timestamp (`ZADD`) and set expire TTL.

---

## 3. Redis Failure Behavior
Redis is treated as an ephemeral cache layer. If Redis connection drops or fails:
- Cache reads fail gracefully and fall back to PostgreSQL / OpenSearch.
- Rate limiting middleware logs warning and allows request execution (fails open).
- **Core database transaction and order data is NEVER lost or corrupted.**

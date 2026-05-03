from __future__ import annotations

import json
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import setting

_redis: Optional[aioredis.Redis] = None

IMAGE_TTL_PENDING = 3
IMAGE_TTL_DONE = 60


async def init_cache() -> None:
    global _redis
    _redis = aioredis.from_url(setting.redis_url, decode_responses=True)


async def close_cache() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


def _client() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis cache не инициализирован — вызовите init_cache()")
    return _redis


async def cache_get(key: str) -> Optional[Any]:
    try:
        raw = await _client().get(key)
        return json.loads(raw) if raw is not None else None
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: int) -> None:
    try:
        await _client().set(key, json.dumps(value, default=str), ex=ttl)
    except Exception:
        pass


async def cache_delete(key: str) -> None:
    try:
        await _client().delete(key)
    except Exception:
        pass

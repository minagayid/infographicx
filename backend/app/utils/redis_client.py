"""Async Redis client accessor.

A single lazily-created ``redis.asyncio`` client is shared across the app.
Creation is deferred until first use so importing this module never opens a
connection — importing the app (and running tests) works with no Redis
running. Callers get the client via :func:`get_redis_client`.
"""
from __future__ import annotations

from typing import Optional

from app.core.config import settings

try:  # redis is an optional import at module load
    from redis.asyncio import Redis, from_url
except Exception:  # pragma: no cover - redis not installed
    Redis = None  # type: ignore
    from_url = None  # type: ignore

_client: "Optional[Redis]" = None


async def get_redis_client() -> "Redis":
    """Return the shared async Redis client, creating it on first use."""
    global _client
    if from_url is None:
        raise RuntimeError("redis package is not installed; cannot create client")
    if _client is None:
        _client = from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    return _client


async def close_redis_client() -> None:
    """Close the shared client (used on app shutdown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None

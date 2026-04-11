"""
Redis client singleton and cache helper functions.

Provides:
    get_redis()              Returns the shared Redis client instance.
    cache_get(key)           Returns the decoded value or None on a miss.
    cache_set(key, val, ttl) Serialises val to JSON and stores with TTL (seconds).
    cache_del(key)           Deletes a single key (call on mutations).
    cache_del_pattern(pat)   Deletes all keys matching a glob pattern (SCAN-based).

Cache failures are logged as warnings and never raise into the request path.

Owner: Camarly Thomas
"""

import json
import logging

import redis

from app.config import REDIS_URL

logger = logging.getLogger(__name__)

_client: "redis.Redis | None" = None


def get_redis() -> redis.Redis:
    """Return the module-level Redis client, creating it on first call."""
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client


def cache_get(key: str):
    """Return the JSON-decoded value stored at `key`, or None on miss/error."""
    try:
        raw = get_redis().get(key)
    except redis.RedisError as exc:
        logger.warning("cache_get(%s) failed: %s", key, exc)
        return None
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError) as exc:
        logger.warning("cache_get(%s) bad JSON: %s", key, exc)
        return None


def cache_set(key: str, value, ttl: int) -> None:
    """Serialise `value` to JSON and store it at `key` for `ttl` seconds."""
    try:
        payload = json.dumps(value, default=str)
        get_redis().setex(key, ttl, payload)
    except (redis.RedisError, TypeError, ValueError) as exc:
        logger.warning("cache_set(%s) failed: %s", key, exc)


def cache_del(key: str) -> None:
    """Delete a single key. Safe to call for a key that doesn't exist."""
    try:
        get_redis().delete(key)
    except redis.RedisError as exc:
        logger.warning("cache_del(%s) failed: %s", key, exc)


def cache_del_pattern(pattern: str) -> None:
    """Delete every key matching a glob pattern using SCAN (not KEYS)."""
    try:
        client = get_redis()
        for key in client.scan_iter(match=pattern, count=500):
            client.delete(key)
    except redis.RedisError as exc:
        logger.warning("cache_del_pattern(%s) failed: %s", pattern, exc)

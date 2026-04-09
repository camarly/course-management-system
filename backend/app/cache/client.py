"""
Redis client singleton and cache helper functions.

Provides:
    get_redis()              Returns the shared Redis client instance.
    cache_get(key)           Returns the decoded value or None on a miss.
    cache_set(key, val, ttl) Serialises val to JSON and stores with TTL (seconds).
    cache_del(key)           Deletes a single key (call on mutations).
    cache_del_pattern(pat)   Deletes all keys matching a glob pattern.

Owner: Camarly Thomas
"""

import os
import json
import redis

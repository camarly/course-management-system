"""
Cache package.

Exposes cache_get() and cache_set() backed by Redis.
Import these helpers from any route or service — do not instantiate
the Redis client directly outside this package.
"""

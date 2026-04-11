"""
Tests for the Redis cache helpers.

Uses the `fake_redis` fixture from conftest.py — no live Redis required.
"""

from app.cache.client import (
    cache_del,
    cache_del_pattern,
    cache_get,
    cache_set,
)
from app.cache import keys as cache_keys


class TestCacheClient:
    def test_set_then_get_roundtrip(self, fake_redis):
        cache_set("unit:test", {"n": 1}, ttl=30)
        assert cache_get("unit:test") == {"n": 1}

    def test_get_miss_returns_none(self, fake_redis):
        assert cache_get("nope") is None

    def test_del_removes_key(self, fake_redis):
        cache_set("k", "v", ttl=30)
        cache_del("k")
        assert cache_get("k") is None

    def test_del_pattern_removes_matching(self, fake_redis):
        cache_set("lms:course:1", {"a": 1}, 30)
        cache_set("lms:course:2", {"a": 2}, 30)
        cache_set("lms:user:1", {"u": 1}, 30)
        cache_del_pattern("lms:course:*")
        assert cache_get("lms:course:1") is None
        assert cache_get("lms:course:2") is None
        assert cache_get("lms:user:1") == {"u": 1}


class TestCacheKeys:
    def test_builders_use_lms_prefix(self):
        assert cache_keys.course_key(42) == "lms:course:42"
        assert cache_keys.course_members_key(7) == "lms:course:7:members"
        assert cache_keys.user_key(1) == "lms:user:1"
        assert cache_keys.thread_key(9) == "lms:thread:9"

    def test_static_keys_defined(self):
        assert cache_keys.COURSES_ALL == "lms:courses:all"
        assert cache_keys.REPORT_TOP10_STUDENTS.startswith("lms:reports:")

"""
Pytest configuration and shared fixtures.

The fixtures in this file let the entire test suite run with NO live
MySQL or Redis — everything is patched in-process. Integration-style
tests that need real services should live under tests/integration/
and skip when the services aren't reachable.

Fixtures:
    fake_db      — in-memory SQL stand-in for get_connection()
    fake_redis   — in-memory stand-in for the Redis cache client
    app          — Flask application with both fakes wired up
    client       — Flask test client for the `app` fixture
    make_token   — helper that signs a JWT for any (id, role) pair
    auth_header  — helper that builds an Authorization header

Owner: Camarly Thomas
"""

from __future__ import annotations

import os
import re
from typing import Any

import pytest

# Make sure config validation passes before `app` is imported. These are
# safe dummy values — tests never hit a real network.
os.environ.setdefault("RUN_MIGRATIONS", "0")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_NAME", "lms_test")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("JWT_EXPIRY_HOURS", "1")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/14")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/13")


# --------------------------------------------------------------------- #
# Fake MySQL                                                            #
# --------------------------------------------------------------------- #

class _FakeCursor:
    """Pattern-matches the handful of SQL shapes used in Phase 1 services."""

    def __init__(self, store: "_FakeDB"):
        self._store = store
        self._result: list[dict] = []
        self.lastrowid: int | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql: str, params: tuple | list = ()):
        sql_norm = " ".join(sql.strip().split())
        params = tuple(params) if params else ()
        self._result = []
        self.lastrowid = None

        # INSERT users
        if sql_norm.startswith("INSERT INTO users"):
            username, email, password_hash, role = params
            if any(u["username"] == username or u["email"] == email
                   for u in self._store.users.values()):
                import pymysql
                raise pymysql.err.IntegrityError(1062, "duplicate")
            new_id = self._store.next_id
            self._store.next_id += 1
            self._store.users[new_id] = {
                "id": new_id,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "role": role,
                "created_at": "2026-04-10T00:00:00",
            }
            self.lastrowid = new_id
            return

        # SELECT ... FROM users WHERE username = %s
        if re.search(r"FROM users WHERE username = %s", sql_norm):
            (username,) = params
            for u in self._store.users.values():
                if u["username"] == username:
                    self._result = [dict(u)]
                    return
            return

        # SELECT ... FROM users WHERE id = %s
        if re.search(r"FROM users WHERE id = %s", sql_norm):
            (user_id,) = params
            u = self._store.users.get(user_id)
            if u:
                self._result = [{k: v for k, v in u.items() if k != "password_hash"}]
            return

        # SELECT ... FROM users ORDER BY id
        if re.search(r"FROM users ORDER BY id", sql_norm):
            self._result = [
                {k: v for k, v in u.items() if k != "password_hash"}
                for u in sorted(self._store.users.values(), key=lambda x: x["id"])
            ]
            return

        raise AssertionError(f"Unhandled fake SQL: {sql_norm}")

    def fetchone(self):
        return self._result[0] if self._result else None

    def fetchall(self):
        return list(self._result)


class _FakeConn:
    def __init__(self, store: "_FakeDB"):
        self._store = store
        self.committed = False
        self.closed = False

    def cursor(self):
        return _FakeCursor(self._store)

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


class _FakeDB:
    def __init__(self):
        self.users: dict[int, dict] = {}
        self.next_id = 1

    def connect(self) -> _FakeConn:
        return _FakeConn(self)


@pytest.fixture
def fake_db(monkeypatch) -> _FakeDB:
    store = _FakeDB()
    # Patch every import location services use.
    from app.db import connection as conn_mod
    from app.services import auth_service, user_service

    monkeypatch.setattr(conn_mod, "get_connection", store.connect)
    monkeypatch.setattr(auth_service, "get_connection", store.connect)
    monkeypatch.setattr(user_service, "get_connection", store.connect)
    return store


# --------------------------------------------------------------------- #
# Fake Redis                                                            #
# --------------------------------------------------------------------- #

class _FakeRedis:
    def __init__(self):
        self.store: dict[str, str] = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value

    def delete(self, *keys):
        for k in keys:
            self.store.pop(k, None)

    def scan_iter(self, match=None, count=500):
        import fnmatch
        for k in list(self.store.keys()):
            if match is None or fnmatch.fnmatch(k, match):
                yield k


@pytest.fixture
def fake_redis(monkeypatch) -> _FakeRedis:
    fake = _FakeRedis()
    from app.cache import client as cache_mod

    monkeypatch.setattr(cache_mod, "_client", fake, raising=False)
    monkeypatch.setattr(cache_mod, "get_redis", lambda: fake)
    return fake


# --------------------------------------------------------------------- #
# Flask app + client                                                    #
# --------------------------------------------------------------------- #

@pytest.fixture
def app(fake_db, fake_redis):
    from app import create_app
    application = create_app()
    application.config.update(TESTING=True)
    return application


@pytest.fixture
def client(app):
    return app.test_client()


# --------------------------------------------------------------------- #
# Token helpers                                                         #
# --------------------------------------------------------------------- #

@pytest.fixture
def make_token():
    from app.services.auth_service import create_token
    return create_token


@pytest.fixture
def auth_header(make_token):
    def _build(user_id: int, role: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {make_token(user_id, role)}"}
    return _build

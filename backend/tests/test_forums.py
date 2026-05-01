"""
First-PR tests for Tramonique Wellington — Forums.

These tests verify the route layer for Tramonique's FIRST set of TODOs:

    1. POST /api/courses/<course_id>/forums  Lecturer/admin creates a forum
    2. GET  /api/courses/<course_id>/forums  Any logged-in user lists forums

Threads and nested replies come in the follow-up PR.

How to pass these tests:
    1. Implement `forum_service.create_forum(course_id, title, description, created_by)`
       → returns the inserted forum dict.
    2. Implement `forum_service.list_forums(course_id)` → returns list[dict].
    3. Wire the two routes in `routes/forums.py` using @require_role.
       Return the standard envelope { "data": ..., "message": ... }.

Run:
    docker compose exec api pytest tests/test_forums.py -v
"""

import pytest

from app.services import forum_service, thread_service, reply_service


class TestCreateForum:
    def test_requires_auth(self, client):
        assert client.post("/api/courses/1/forums", json={"title": "General"}).status_code == 401

    def test_student_forbidden(self, client, auth_header):
        r = client.post(
            "/api/courses/1/forums",
            headers=auth_header(1, "student"),
            json={"title": "General"},
        )
        assert r.status_code == 403

    def test_lecturer_creates_forum(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            forum_service, "create_forum",
            lambda **kw: {"id": 1, **kw},
        )
        r = client.post(
            "/api/courses/1/forums",
            headers=auth_header(2, "lecturer"),
            json={"title": "General", "description": "Ask anything"},
        )
        assert r.status_code == 201
        assert r.get_json()["data"]["title"] == "General"


class TestListForums:
    def test_requires_auth(self, client):
        assert client.get("/api/courses/1/forums").status_code == 401

    def test_returns_forum_list(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            forum_service, "list_forums",
            lambda cid: [{"id": 1, "course_id": cid, "title": "General"}],
        )
        r = client.get("/api/courses/1/forums", headers=auth_header(1, "student"))
        assert r.status_code == 200
        assert r.get_json()["data"][0]["title"] == "General"


class TestThreads:
    def test_create_requires_auth(self, client):
        assert client.post(
            "/api/forums/1/threads",
            json={"title": "Q1", "body": "..."},
        ).status_code == 401

    def test_create_missing_fields_returns_400(self, client, auth_header):
        r = client.post(
            "/api/forums/1/threads",
            headers=auth_header(1, "student"),
            json={"title": "Only title"},
        )
        assert r.status_code == 400

    def test_student_creates_thread(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            thread_service, "create_thread",
            lambda **kw: {"id": 1, **kw},
        )
        r = client.post(
            "/api/forums/1/threads",
            headers=auth_header(1, "student"),
            json={"title": "Q1", "body": "Question text"},
        )
        assert r.status_code == 201
        assert r.get_json()["data"]["title"] == "Q1"

    def test_list_requires_auth(self, client):
        assert client.get("/api/forums/1/threads").status_code == 401

    def test_list_threads(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            thread_service, "list_threads",
            lambda fid: [{"id": 1, "forum_id": fid, "title": "Q1"}],
        )
        r = client.get("/api/forums/1/threads", headers=auth_header(1, "student"))
        assert r.status_code == 200
        assert r.get_json()["data"][0]["forum_id"] == 1

    def test_get_thread_404_when_missing(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(thread_service, "get_thread_with_replies", lambda tid: None)
        r = client.get("/api/threads/999", headers=auth_header(1, "student"))
        assert r.status_code == 404

    def test_get_thread_returns_nested(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            thread_service, "get_thread_with_replies",
            lambda tid: {"id": tid, "title": "Q1", "replies": [{"id": 10, "replies": []}]},
        )
        r = client.get("/api/threads/1", headers=auth_header(1, "student"))
        assert r.status_code == 200
        assert r.get_json()["data"]["replies"][0]["id"] == 10


class TestReplies:
    def test_top_level_requires_auth(self, client):
        assert client.post(
            "/api/threads/1/replies",
            json={"body": "reply"},
        ).status_code == 401

    def test_top_level_missing_body_returns_400(self, client, auth_header):
        r = client.post(
            "/api/threads/1/replies",
            headers=auth_header(1, "student"),
            json={},
        )
        assert r.status_code == 400

    def test_student_replies_to_thread(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            reply_service, "create_reply",
            lambda **kw: {"id": 1, **kw},
        )
        r = client.post(
            "/api/threads/5/replies",
            headers=auth_header(1, "student"),
            json={"body": "Reply text"},
        )
        assert r.status_code == 201
        data = r.get_json()["data"]
        assert data["thread_id"] == 5
        assert data["parent_reply_id"] is None

    def test_nested_reply_404_when_parent_missing(self, client, auth_header, monkeypatch):
        from app.db import connection as connection_mod

        class _Cur:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def execute(self, sql, params): pass
            def fetchone(self): return None

        class _Conn:
            def cursor(self): return _Cur()
            def close(self): pass

        monkeypatch.setattr(connection_mod, "get_connection", lambda: _Conn())
        r = client.post(
            "/api/replies/999/replies",
            headers=auth_header(1, "student"),
            json={"body": "sub-reply"},
        )
        assert r.status_code == 404

    def test_nested_reply_created(self, client, auth_header, monkeypatch):
        from app.db import connection as connection_mod

        class _Cur:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def execute(self, sql, params): pass
            def fetchone(self): return {"thread_id": 7}

        class _Conn:
            def cursor(self): return _Cur()
            def close(self): pass

        monkeypatch.setattr(connection_mod, "get_connection", lambda: _Conn())
        monkeypatch.setattr(
            reply_service, "create_reply",
            lambda **kw: {"id": 99, **kw},
        )
        r = client.post(
            "/api/replies/42/replies",
            headers=auth_header(1, "student"),
            json={"body": "nested"},
        )
        assert r.status_code == 201
        data = r.get_json()["data"]
        assert data["thread_id"] == 7
        assert data["parent_reply_id"] == 42

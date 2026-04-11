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

from app.services import forum_service


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


# The placeholders below are kept so `pytest --collect-only` still groups
# the Thread and Reply tests — fill in in the next PR.

class TestThreads:
    def test_placeholder(self):
        pytest.skip("Threads come in Tramonique's second PR")


class TestReplies:
    def test_placeholder(self):
        pytest.skip("Nested replies come in Tramonique's second PR")

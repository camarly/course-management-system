"""
First-PR tests for Tamarica Shaw — Courses.

These tests verify the route layer, auth guards, and response envelope
for Tamarica's FIRST set of TODOs:

    1. POST /api/courses                Admin creates a course
    2. GET  /api/courses                List all courses (any logged-in user)
    3. GET  /api/courses/<course_id>    Get a single course by ID

The service layer is patched — these tests do NOT hit MySQL. Once the
route + service wiring is in place, all tests pass. Deeper SQL tests
come later.

How to pass these tests:
    1. Implement `course_service.create_course(title, description, lecturer_id)`
    2. Implement `course_service.list_courses()`
    3. Implement `course_service.get_course(course_id)`  (returns dict or None)
    4. Wire the three routes in `routes/courses.py`, using @require_role
       and returning the standard envelope { "data": ..., "message": ... }.

Run:
    docker compose exec api pytest tests/test_courses.py -v
    # or, outside Docker:
    cd backend && source .venv/bin/activate && pytest tests/test_courses.py -v
"""

import pytest

from app.services import course_service


class TestCreateCourse:
    def test_requires_auth(self, client):
        r = client.post("/api/courses", json={"title": "COMP3161"})
        assert r.status_code == 401

    def test_student_forbidden(self, client, auth_header):
        r = client.post(
            "/api/courses",
            headers=auth_header(1, "student"),
            json={"title": "COMP3161", "description": "DB Systems"},
        )
        assert r.status_code == 403

    def test_admin_creates_course(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            course_service, "create_course",
            lambda **kw: {"id": 1, **kw},
        )
        r = client.post(
            "/api/courses",
            headers=auth_header(1, "admin"),
            json={"title": "COMP3161", "description": "DB Systems", "lecturer_id": 2},
        )
        assert r.status_code == 201
        assert r.get_json()["data"]["title"] == "COMP3161"


class TestListCourses:
    def test_requires_auth(self, client):
        assert client.get("/api/courses").status_code == 401

    def test_list_returns_array(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            course_service, "list_courses",
            lambda: [{"id": 1, "title": "COMP3161"}],
        )
        r = client.get("/api/courses", headers=auth_header(1, "student"))
        assert r.status_code == 200
        assert isinstance(r.get_json()["data"], list)
        assert r.get_json()["data"][0]["title"] == "COMP3161"


class TestGetCourse:
    def test_returns_404_when_missing(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(course_service, "get_course", lambda cid: None)
        r = client.get("/api/courses/999", headers=auth_header(1, "student"))
        assert r.status_code == 404

    def test_returns_course_on_hit(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            course_service, "get_course",
            lambda cid: {"id": cid, "title": "COMP3161"},
        )
        r = client.get("/api/courses/1", headers=auth_header(1, "student"))
        assert r.status_code == 200
        assert r.get_json()["data"]["id"] == 1

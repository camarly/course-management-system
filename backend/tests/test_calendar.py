"""
Calendar tests — Tamarica Shaw.

Covers:
    POST /api/courses/<course_id>/events
    GET  /api/courses/<course_id>/events
    GET  /api/students/<student_id>/events?date=YYYY-MM-DD
"""

from app.services import calendar_service


class TestCreateEvent:
    def test_requires_auth(self, client):
        assert client.post(
            "/api/courses/1/events",
            json={"title": "Quiz", "event_date": "2026-05-10"},
        ).status_code == 401

    def test_student_forbidden(self, client, auth_header):
        r = client.post(
            "/api/courses/1/events",
            headers=auth_header(1, "student"),
            json={"title": "Quiz", "event_date": "2026-05-10"},
        )
        assert r.status_code == 403

    def test_missing_fields_returns_400(self, client, auth_header):
        r = client.post(
            "/api/courses/1/events",
            headers=auth_header(2, "lecturer"),
            json={"title": "Quiz"},
        )
        assert r.status_code == 400

    def test_lecturer_creates_event(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            calendar_service, "create_event",
            lambda **kw: {"id": 1, **kw},
        )
        r = client.post(
            "/api/courses/1/events",
            headers=auth_header(2, "lecturer"),
            json={
                "title": "Quiz 1",
                "event_date": "2026-05-10",
                "event_time": "14:00",
                "description": "covers ch 1-3",
            },
        )
        assert r.status_code == 201
        assert r.get_json()["data"]["title"] == "Quiz 1"


class TestListCourseEvents:
    def test_requires_auth(self, client):
        assert client.get("/api/courses/1/events").status_code == 401

    def test_returns_events(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            calendar_service, "list_events",
            lambda cid: [{"id": 1, "course_id": cid, "title": "Quiz 1"}],
        )
        r = client.get("/api/courses/1/events", headers=auth_header(1, "student"))
        assert r.status_code == 200
        assert r.get_json()["data"][0]["course_id"] == 1


class TestStudentEvents:
    def test_requires_auth(self, client):
        assert client.get("/api/students/1/events?date=2026-05-10").status_code == 401

    def test_lecturer_forbidden(self, client, auth_header):
        r = client.get(
            "/api/students/1/events?date=2026-05-10",
            headers=auth_header(2, "lecturer"),
        )
        assert r.status_code == 403

    def test_missing_date_returns_400(self, client, auth_header):
        r = client.get("/api/students/1/events", headers=auth_header(1, "student"))
        assert r.status_code == 400

    def test_returns_events_on_date(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            calendar_service, "list_student_events_on_date",
            lambda sid, date: [{"id": 1, "title": "Quiz 1", "event_date": date}],
        )
        r = client.get(
            "/api/students/1/events?date=2026-05-10",
            headers=auth_header(1, "student"),
        )
        assert r.status_code == 200
        assert r.get_json()["data"][0]["event_date"] == "2026-05-10"

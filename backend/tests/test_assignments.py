"""
First-PR tests for Carl Heron — Assignments.

These tests cover Carl's FIRST set of TODOs:

    1. POST /api/courses/<course_id>/assignments  Lecturer creates assignment
    2. GET  /api/courses/<course_id>/assignments  Any logged-in user lists them
    3. GET  /api/assignments/<assignment_id>      Get a single assignment

Submissions, grading, and reports come in follow-up PRs.

How to pass these tests:
    1. Implement `assignment_service.create_assignment(course_id, title, due_date, weight, description)`
    2. Implement `assignment_service.list_for_course(course_id)`
    3. Implement `assignment_service.get_assignment(assignment_id)` → dict or None
    4. Wire `routes/assignments.py` with @require_role.

Run:
    docker compose exec api pytest tests/test_assignments.py -v
"""

import pytest

from app.services import assignment_service, submission_service, grade_service


class TestCreateAssignment:
    def test_requires_auth(self, client):
        assert client.post(
            "/api/courses/1/assignments",
            json={"title": "HW1"},
        ).status_code == 401

    def test_student_forbidden(self, client, auth_header):
        r = client.post(
            "/api/courses/1/assignments",
            headers=auth_header(1, "student"),
            json={"title": "HW1", "due_date": "2026-05-01T00:00:00", "weight": 20},
        )
        assert r.status_code == 403

    def test_lecturer_creates(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            assignment_service, "create_assignment",
            lambda **kw: {"id": 1, **kw},
        )
        r = client.post(
            "/api/courses/1/assignments",
            headers=auth_header(2, "lecturer"),
            json={
                "title": "HW1",
                "description": "First homework",
                "due_date": "2026-05-01T00:00:00",
                "weight": 20,
            },
        )
        assert r.status_code == 201
        assert r.get_json()["data"]["title"] == "HW1"


class TestListAssignments:
    def test_requires_auth(self, client):
        assert client.get("/api/courses/1/assignments").status_code == 401

    def test_returns_list(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            assignment_service, "list_for_course",
            lambda cid: [{"id": 1, "course_id": cid, "title": "HW1"}],
        )
        r = client.get("/api/courses/1/assignments", headers=auth_header(1, "student"))
        assert r.status_code == 200
        assert r.get_json()["data"][0]["title"] == "HW1"


class TestGetAssignment:
    def test_404_when_missing(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(assignment_service, "get_assignment", lambda aid: None)
        r = client.get("/api/assignments/999", headers=auth_header(1, "student"))
        assert r.status_code == 404

    def test_200_when_hit(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            assignment_service, "get_assignment",
            lambda aid: {"id": aid, "title": "HW1"},
        )
        r = client.get("/api/assignments/1", headers=auth_header(1, "student"))
        assert r.status_code == 200
        assert r.get_json()["data"]["id"] == 1


class TestSubmissions:
    def test_submit_requires_auth(self, client):
        assert client.post(
            "/api/assignments/1/submit",
            json={"file_url": "s3://x"},
        ).status_code == 401

    def test_lecturer_cannot_submit(self, client, auth_header):
        r = client.post(
            "/api/assignments/1/submit",
            headers=auth_header(2, "lecturer"),
            json={"file_url": "s3://x"},
        )
        assert r.status_code == 403

    def test_missing_file_url_returns_400(self, client, auth_header):
        r = client.post(
            "/api/assignments/1/submit",
            headers=auth_header(1, "student"),
            json={},
        )
        assert r.status_code == 400

    def test_student_submits(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            submission_service, "submit",
            lambda **kw: {"id": 1, **kw},
        )
        r = client.post(
            "/api/assignments/1/submit",
            headers=auth_header(1, "student"),
            json={"file_url": "s3://hw1.pdf"},
        )
        assert r.status_code == 201
        assert r.get_json()["data"]["file_url"] == "s3://hw1.pdf"

    def test_duplicate_submission_returns_409(self, client, auth_header, monkeypatch):
        def _raise(**kw):
            raise ValueError("duplicate_submission")
        monkeypatch.setattr(submission_service, "submit", _raise)
        r = client.post(
            "/api/assignments/1/submit",
            headers=auth_header(1, "student"),
            json={"file_url": "s3://hw1.pdf"},
        )
        assert r.status_code == 409

    def test_list_submissions_forbidden_for_student(self, client, auth_header):
        r = client.get(
            "/api/assignments/1/submissions",
            headers=auth_header(1, "student"),
        )
        assert r.status_code == 403

    def test_lecturer_lists_submissions(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            submission_service, "list_submissions",
            lambda aid: [{"id": 1, "assignment_id": aid, "student_id": 1}],
        )
        r = client.get(
            "/api/assignments/1/submissions",
            headers=auth_header(2, "lecturer"),
        )
        assert r.status_code == 200
        assert r.get_json()["data"][0]["assignment_id"] == 1

    def test_student_grades_returns_list(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            submission_service, "list_student_grades",
            lambda sid: [{"assignment_id": 1, "score": 87.5}],
        )
        r = client.get(
            "/api/students/1/grades",
            headers=auth_header(1, "student"),
        )
        assert r.status_code == 200
        assert r.get_json()["data"][0]["score"] == 87.5


class TestGrades:
    def test_requires_auth(self, client):
        assert client.post(
            "/api/submissions/1/grade",
            json={"score": 90},
        ).status_code == 401

    def test_student_forbidden(self, client, auth_header):
        r = client.post(
            "/api/submissions/1/grade",
            headers=auth_header(1, "student"),
            json={"score": 90},
        )
        assert r.status_code == 403

    def test_missing_score_returns_400(self, client, auth_header):
        r = client.post(
            "/api/submissions/1/grade",
            headers=auth_header(2, "lecturer"),
            json={},
        )
        assert r.status_code == 400

    def test_lecturer_records_grade(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            grade_service, "record_grade",
            lambda **kw: {"id": 1, **kw},
        )
        r = client.post(
            "/api/submissions/1/grade",
            headers=auth_header(2, "lecturer"),
            json={"score": 92, "feedback": "Solid work"},
        )
        assert r.status_code == 201
        assert r.get_json()["data"]["score"] == 92

    def test_submission_not_found_returns_404(self, client, auth_header, monkeypatch):
        def _raise(**kw):
            raise ValueError("submission_not_found")
        monkeypatch.setattr(grade_service, "record_grade", _raise)
        r = client.post(
            "/api/submissions/999/grade",
            headers=auth_header(2, "lecturer"),
            json={"score": 90},
        )
        assert r.status_code == 404

    def test_already_graded_returns_409(self, client, auth_header, monkeypatch):
        def _raise(**kw):
            raise ValueError("already_graded")
        monkeypatch.setattr(grade_service, "record_grade", _raise)
        r = client.post(
            "/api/submissions/1/grade",
            headers=auth_header(2, "lecturer"),
            json={"score": 90},
        )
        assert r.status_code == 409

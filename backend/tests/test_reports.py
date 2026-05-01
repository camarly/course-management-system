"""
Reports tests — Carl Heron.

Covers the five admin-only report endpoints. Each one is cached, so we
verify both the miss path (calls report_service) and that the result
flows through the standard envelope.
"""

from app.services import report_service


class TestReportsAuth:
    def test_requires_auth(self, client):
        assert client.get("/api/reports/courses-50-plus").status_code == 401

    def test_lecturer_forbidden(self, client, auth_header):
        r = client.get(
            "/api/reports/courses-50-plus",
            headers=auth_header(2, "lecturer"),
        )
        assert r.status_code == 403

    def test_student_forbidden(self, client, auth_header):
        r = client.get(
            "/api/reports/top10-students-by-average",
            headers=auth_header(1, "student"),
        )
        assert r.status_code == 403


class TestReportEndpoints:
    def test_courses_50_plus(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            report_service, "courses_50_plus",
            lambda: [{"course_id": 1, "title": "DB Systems", "enrolled": 120}],
        )
        r = client.get(
            "/api/reports/courses-50-plus",
            headers=auth_header(99, "admin"),
        )
        assert r.status_code == 200
        assert r.get_json()["data"][0]["enrolled"] == 120

    def test_students_5_plus_courses(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            report_service, "students_5_plus_courses",
            lambda: [{"student_id": 1, "course_count": 6}],
        )
        r = client.get(
            "/api/reports/students-5-plus-courses",
            headers=auth_header(99, "admin"),
        )
        assert r.status_code == 200
        assert r.get_json()["data"][0]["course_count"] == 6

    def test_lecturers_3_plus_courses(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            report_service, "lecturers_3_plus_courses",
            lambda: [{"lecturer_id": 5, "course_count": 4}],
        )
        r = client.get(
            "/api/reports/lecturers-3-plus-courses",
            headers=auth_header(99, "admin"),
        )
        assert r.status_code == 200
        assert r.get_json()["data"][0]["lecturer_id"] == 5

    def test_top10_enrolled_courses(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            report_service, "top10_enrolled_courses",
            lambda: [{"course_id": i, "enrolled": 100 - i} for i in range(10)],
        )
        r = client.get(
            "/api/reports/top10-enrolled-courses",
            headers=auth_header(99, "admin"),
        )
        assert r.status_code == 200
        assert len(r.get_json()["data"]) == 10

    def test_top10_students_by_average(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            report_service, "top10_students_by_average",
            lambda: [{"student_id": 1, "average": 95.5}],
        )
        r = client.get(
            "/api/reports/top10-students-by-average",
            headers=auth_header(99, "admin"),
        )
        assert r.status_code == 200
        assert r.get_json()["data"][0]["average"] == 95.5


class TestReportsCaching:
    def test_second_call_served_from_cache(self, client, auth_header, monkeypatch):
        calls = {"n": 0}

        def fetch():
            calls["n"] += 1
            return [{"course_id": 1, "enrolled": 80}]

        monkeypatch.setattr(report_service, "courses_50_plus", fetch)

        r1 = client.get(
            "/api/reports/courses-50-plus",
            headers=auth_header(99, "admin"),
        )
        r2 = client.get(
            "/api/reports/courses-50-plus",
            headers=auth_header(99, "admin"),
        )
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert calls["n"] == 1

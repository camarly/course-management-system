"""
Report routes.

All endpoints are admin-only and read directly from the SQL Views
defined in migration 014.

Endpoints:
    GET  /api/reports/courses-50-plus              Courses with >= 50 enrolled students
    GET  /api/reports/students-5-plus-courses      Students enrolled in >= 5 courses
    GET  /api/reports/lecturers-3-plus-courses     Lecturers teaching >= 3 courses
    GET  /api/reports/top10-enrolled-courses       Top 10 most enrolled courses
    GET  /api/reports/top10-students-by-average    Top 10 students by average grade

Owner: Carl Heron
"""

from flask import Blueprint, jsonify
from app.middleware.roles import require_role
from app.services import report_service
from app.cache.client import cache_get, cache_set
from app.cache.keys import (
    REPORT_COURSES_50_PLUS,
    REPORT_STUDENTS_5_PLUS,
    REPORT_LECTURERS_3_PLUS,
    REPORT_TOP10_COURSES,
    REPORT_TOP10_STUDENTS,
    TTL_MEDIUM,
)

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


def _cached_report(cache_key, fetch_fn):
    hit = cache_get(cache_key)
    if hit is not None:
        return jsonify({"data": hit, "message": None}), 200
    data = fetch_fn()
    cache_set(cache_key, data, TTL_MEDIUM)
    return jsonify({"data": data, "message": None}), 200


@reports_bp.route("/courses-50-plus", methods=["GET"])
@require_role("admin")
def courses_50_plus(current_user):
    return _cached_report(REPORT_COURSES_50_PLUS, report_service.courses_50_plus)


@reports_bp.route("/students-5-plus-courses", methods=["GET"])
@require_role("admin")
def students_5_plus_courses(current_user):
    return _cached_report(REPORT_STUDENTS_5_PLUS, report_service.students_5_plus_courses)


@reports_bp.route("/lecturers-3-plus-courses", methods=["GET"])
@require_role("admin")
def lecturers_3_plus_courses(current_user):
    return _cached_report(REPORT_LECTURERS_3_PLUS, report_service.lecturers_3_plus_courses)


@reports_bp.route("/top10-enrolled-courses", methods=["GET"])
@require_role("admin")
def top10_enrolled_courses(current_user):
    return _cached_report(REPORT_TOP10_COURSES, report_service.top10_enrolled_courses)


@reports_bp.route("/top10-students-by-average", methods=["GET"])
@require_role("admin")
def top10_students_by_average(current_user):
    return _cached_report(REPORT_TOP10_STUDENTS, report_service.top10_students_by_average)

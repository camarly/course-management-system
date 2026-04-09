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

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

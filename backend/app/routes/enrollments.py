"""
Enrollment routes.

Endpoints:
    POST  /api/courses/<course_id>/enroll   Student self-enrolls in a course

Enforces:
    - Student may not exceed 6 concurrent enrollments (403)
    - Duplicate enrollment returns 409
    - Course must exist (404)

Owner: Tamarica Shaw
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

enrollments_bp = Blueprint('enrollments', __name__, url_prefix='/api')

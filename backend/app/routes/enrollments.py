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
from app.services import enrollment_service

enrollments_bp = Blueprint('enrollments', __name__, url_prefix='/api')


@enrollments_bp.route("/courses/<int:course_id>/enroll", methods=["POST"])
@require_role("student")
def enroll(course_id, current_user):
    try:
        enrollment = enrollment_service.enroll(current_user["id"], course_id)
    except ValueError as e:
        msg = str(e)
        if msg == "course_not_found":
            return jsonify({"error": "not_found", "message": "Course not found"}), 404
        if msg == "enrollment_limit":
            return jsonify({"error": "enrollment_limit", "message": "Cannot enroll in more than 6 courses"}), 403
        if msg == "duplicate_enrollment":
            return jsonify({"error": "duplicate", "message": "Already enrolled in this course"}), 409
        raise
    return jsonify({"data": enrollment, "message": "Enrolled successfully"}), 201

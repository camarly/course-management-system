"""
Course routes.

Endpoints:
    POST  /api/courses                          Admin: create a course
    GET   /api/courses                          List all courses
    GET   /api/courses/<course_id>              Get a single course
    GET   /api/courses/<course_id>/members      Get all members of a course
    POST  /api/courses/<course_id>/assign-lecturer  Admin: assign a lecturer
    GET   /api/students/<student_id>/courses    Courses for a specific student
    GET   /api/lecturers/<lecturer_id>/courses  Courses for a specific lecturer

Owner: Tamarica Shaw
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role
from app.services import course_service

courses_bp = Blueprint('courses', __name__, url_prefix='/api')


@courses_bp.route("/courses", methods=["POST"])
@require_role("admin")
def create_course(current_user):
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    if not title:
        return jsonify({"error": "missing_fields", "message": "title is required"}), 400
    course = course_service.create_course(
        title=title,
        description=body.get("description"),
        lecturer_id=body.get("lecturer_id"),
    )
    return jsonify({"data": course, "message": "Course created"}), 201


@courses_bp.route("/courses", methods=["GET"])
@require_role("admin", "lecturer", "student")
def list_courses(current_user):
    courses = course_service.list_courses()
    return jsonify({"data": courses, "message": None}), 200


@courses_bp.route("/courses/<int:course_id>", methods=["GET"])
@require_role("admin", "lecturer", "student")
def get_course(course_id, current_user):
    course = course_service.get_course(course_id)
    if not course:
        return jsonify({"error": "not_found", "message": "Course not found"}), 404
    return jsonify({"data": course, "message": None}), 200


@courses_bp.route("/courses/<int:course_id>/members", methods=["GET"])
@require_role("admin", "lecturer", "student")
def get_members(course_id, current_user):
    members = course_service.get_members(course_id)
    return jsonify({"data": members, "message": None}), 200


@courses_bp.route("/courses/<int:course_id>/assign-lecturer", methods=["POST"])
@require_role("admin")
def assign_lecturer(course_id, current_user):
    body = request.get_json(silent=True) or {}
    lecturer_id = body.get("lecturer_id")
    if not lecturer_id:
        return jsonify({"error": "missing_fields", "message": "lecturer_id is required"}), 400
    try:
        course = course_service.assign_lecturer(course_id, lecturer_id)
    except ValueError as e:
        msg = str(e)
        if msg == "not_found":
            return jsonify({"error": "not_found", "message": "Lecturer not found"}), 404
        if msg == "not_lecturer":
            return jsonify({"error": "invalid_role", "message": "User is not a lecturer"}), 400
        if msg == "lecturer_limit":
            return jsonify({"error": "lecturer_limit", "message": "Lecturer already assigned to 5 courses"}), 403
        raise
    return jsonify({"data": course, "message": "Lecturer assigned"}), 200


@courses_bp.route("/students/<int:student_id>/courses", methods=["GET"])
@require_role("admin", "student")
def get_student_courses(student_id, current_user):
    courses = course_service.get_student_courses(student_id)
    return jsonify({"data": courses, "message": None}), 200


@courses_bp.route("/lecturers/<int:lecturer_id>/courses", methods=["GET"])
@require_role("admin", "lecturer")
def get_lecturer_courses(lecturer_id, current_user):
    courses = course_service.get_lecturer_courses(lecturer_id)
    return jsonify({"data": courses, "message": None}), 200

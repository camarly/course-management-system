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


@courses_bp.route('/courses', methods=['POST'])
@require_role('admin')
def create_course(current_user):
    data = request.get_json(silent=True) or {}
    if not data.get('title'):
        return jsonify({
            "error": "missing_fields",
            "message": "title is required",
        }), 400

    course = course_service.create_course(
        title=data['title'],
        description=data.get('description'),
        lecturer_id=data.get('lecturer_id'),
    )
    return jsonify({"data": course, "message": "Course created"}), 201


@courses_bp.route('/courses', methods=['GET'])
@require_role('admin', 'lecturer', 'student')
def list_courses(current_user):
    return jsonify({
        "data": course_service.list_courses(),
        "message": None,
    }), 200


@courses_bp.route('/courses/<int:course_id>', methods=['GET'])
@require_role('admin', 'lecturer', 'student')
def get_course(current_user, course_id):
    course = course_service.get_course(course_id)
    if course is None:
        return jsonify({
            "error": "not_found",
            "message": "Course not found",
        }), 404
    return jsonify({"data": course, "message": "Course retrieved"}), 200



@courses_bp.route('/students/<int:student_id>/courses', methods=['GET'])
@require_role('admin', 'lecturer', 'student')
def get_student_courses(current_user, student_id):
    """
    Get all courses for a specific student.
    
    
    """
    
    if current_user['role'] == 'student' and current_user['id'] != student_id:
        return jsonify({
            "error": "forbidden",
            "message": "Students can only view their own courses"
        }), 403
    
    
    courses = course_service.get_courses_for_student(student_id)
    
    return jsonify({
        "data": courses,
        "message": "Courses retrieved"
    }), 200
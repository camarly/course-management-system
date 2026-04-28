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


@courses_bp.route('/courses/<int:course_id>', methods=['GET'])
@require_role('admin', 'lecturer', 'student')
def get_course(current_user, course_id):
    """
    Get a single course by ID.
    
    """
    course = course_service.get_course(course_id)
    
    if course is None:
        return jsonify({
            "error": "not_found",
            "message": "Course not found"
        }), 404
    
    return jsonify({
        "data": course,
        "message": "Course retrieved"
    }), 200
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
    """
    Create a new course.
    
    Admin only.
    
    
    """
    
    data = request.get_json(silent=True) or {}
    
    # Validate required fields
    if not data.get('title'):
        return jsonify({
            "error": "missing_fields",
            "message": "title is required"
        }), 400
    
    # Call service to create course
    course = course_service.create_course(
        title=data['title'],
        description=data.get('description'),
        lecturer_id=data.get('lecturer_id')
    )
    
    # Return success envelope
    return jsonify({
        "data": course,
        "message": "Course created"
    }), 201


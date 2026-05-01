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





@courses_bp.route('/courses/<int:course_id>/assign-lecturer', methods=['POST'])
@require_role('admin')
def assign_lecturer(current_user, course_id):
    """
    Assign a lecturer to a course.
    
    Admin only.
    Enforces one-lecturer rule and 5-course lecturer cap.
    Replaces any existing assignment.
   "}
    """
    
    data = request.get_json(silent=True) or {}
    
    
    if not data.get('lecturer_id'):
        return jsonify({
            "error": "missing_fields",
            "message": "lecturer_id is required"
        }), 400
    
    try:
        
        course = course_service.assign_lecturer_to_course(
            course_id=course_id,
            lecturer_id=data['lecturer_id']
        )
        
        return jsonify({
            "data": course,
            "message": "Lecturer assigned successfully"
        }), 200
        
    except ValueError as e:
        error_message = str(e)
        
       
        if error_message == "Course not found":
            return jsonify({
                "error": "not_found",
                "message": "Course not found"
            }), 404
        elif error_message == "User not found":
            return jsonify({
                "error": "user_not_found",
                "message": "User not found"
            }), 404
        elif error_message == "User is not a lecturer":
            return jsonify({
                "error": "invalid_role",
                "message": "User is not a lecturer"
            }), 400
        elif "already assigned to 5 courses" in error_message:
            return jsonify({
                "error": "lecturer_cap_reached",
                "message": error_message
            }), 400
        else:
            return jsonify({
                "error": "assignment_failed",
                "message": error_message
            }), 400
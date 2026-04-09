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

courses_bp = Blueprint('courses', __name__, url_prefix='/api')

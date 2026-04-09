"""
Assignment routes.

Endpoints:
    POST  /api/courses/<course_id>/assignments      Lecturer creates an assignment
    GET   /api/courses/<course_id>/assignments      All assignments for a course
    GET   /api/assignments/<assignment_id>          Single assignment detail

Owner: Carl Heron
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

assignments_bp = Blueprint('assignments', __name__, url_prefix='/api')

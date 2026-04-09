"""
Submission routes.

Endpoints:
    POST  /api/assignments/<assignment_id>/submit        Student submits an assignment
    GET   /api/assignments/<assignment_id>/submissions   Lecturer views all submissions
    GET   /api/students/<student_id>/grades              All grades for a student

Owner: Carl Heron
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

submissions_bp = Blueprint('submissions', __name__, url_prefix='/api')

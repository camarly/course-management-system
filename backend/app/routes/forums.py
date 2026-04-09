"""
Forum routes.

Endpoints:
    POST  /api/courses/<course_id>/forums   Lecturer/admin creates a forum
    GET   /api/courses/<course_id>/forums   All forums for a course

Owner: Tramonique Wellington
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

forums_bp = Blueprint('forums', __name__, url_prefix='/api')

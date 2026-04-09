"""
Calendar event routes.

Endpoints:
    POST  /api/courses/<course_id>/events          Create a calendar event
    GET   /api/courses/<course_id>/events          All events for a course
    GET   /api/students/<student_id>/events        Student events on a date (?date=YYYY-MM-DD)

Owner: Tamarica Shaw
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

calendar_bp = Blueprint('calendar', __name__, url_prefix='/api')

"""
Grade routes.

Endpoints:
    POST  /api/submissions/<submission_id>/grade   Lecturer submits a grade

After a grade is written, a Celery task is enqueued to recalculate
the student's average in the student_averages table.

Owner: Carl Heron
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

grades_bp = Blueprint('grades', __name__, url_prefix='/api')

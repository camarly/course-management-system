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
from app.services import grade_service

grades_bp = Blueprint('grades', __name__, url_prefix='/api')


@grades_bp.route("/submissions/<int:submission_id>/grade", methods=["POST"])
@require_role("lecturer")
def grade_submission(submission_id, current_user):
    body = request.get_json(silent=True) or {}
    score = body.get("score")
    if score is None:
        return jsonify({"error": "missing_fields", "message": "score is required"}), 400
    try:
        grade = grade_service.record_grade(
            submission_id=submission_id,
            graded_by=current_user["id"],
            score=score,
            feedback=body.get("feedback"),
        )
    except ValueError as e:
        msg = str(e)
        if msg == "submission_not_found":
            return jsonify({"error": "not_found", "message": "Submission not found"}), 404
        if msg == "already_graded":
            return jsonify({"error": "duplicate", "message": "Submission already graded"}), 409
        raise
    return jsonify({"data": grade, "message": "Grade recorded"}), 201

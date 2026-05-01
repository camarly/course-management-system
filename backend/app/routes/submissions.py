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
from app.services import submission_service

submissions_bp = Blueprint('submissions', __name__, url_prefix='/api')


@submissions_bp.route("/assignments/<int:assignment_id>/submit", methods=["POST"])
@require_role("student")
def submit_assignment(assignment_id, current_user):
    body = request.get_json(silent=True) or {}
    file_url = body.get("file_url")
    if not file_url:
        return jsonify({"error": "missing_fields", "message": "file_url is required"}), 400
    try:
        submission = submission_service.submit(
            assignment_id=assignment_id,
            student_id=current_user["id"],
            file_url=file_url,
        )
    except ValueError as e:
        if str(e) == "duplicate_submission":
            return jsonify({"error": "duplicate", "message": "Already submitted this assignment"}), 409
        raise
    return jsonify({"data": submission, "message": "Submission received"}), 201


@submissions_bp.route("/assignments/<int:assignment_id>/submissions", methods=["GET"])
@require_role("lecturer", "admin")
def list_submissions(assignment_id, current_user):
    submissions = submission_service.list_submissions(assignment_id)
    return jsonify({"data": submissions, "message": None}), 200


@submissions_bp.route("/students/<int:student_id>/grades", methods=["GET"])
@require_role("student", "admin")
def student_grades(student_id, current_user):
    grades = submission_service.list_student_grades(student_id)
    return jsonify({"data": grades, "message": None}), 200

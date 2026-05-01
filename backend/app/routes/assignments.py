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
from app.services import assignment_service

assignments_bp = Blueprint('assignments', __name__, url_prefix='/api')


@assignments_bp.route("/courses/<int:course_id>/assignments", methods=["POST"])
@require_role("lecturer", "admin")
def create_assignment(course_id, current_user):
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    due_date = body.get("due_date")
    weight = body.get("weight")
    if not title or due_date is None or weight is None:
        return jsonify({"error": "missing_fields", "message": "title, due_date, weight required"}), 400
    assignment = assignment_service.create_assignment(
        course_id=course_id,
        title=title,
        due_date=due_date,
        weight=weight,
        description=body.get("description"),
    )
    return jsonify({"data": assignment, "message": "Assignment created"}), 201


@assignments_bp.route("/courses/<int:course_id>/assignments", methods=["GET"])
@require_role("admin", "lecturer", "student")
def list_assignments(course_id, current_user):
    assignments = assignment_service.list_for_course(course_id)
    return jsonify({"data": assignments, "message": None}), 200


@assignments_bp.route("/assignments/<int:assignment_id>", methods=["GET"])
@require_role("admin", "lecturer", "student")
def get_assignment(assignment_id, current_user):
    assignment = assignment_service.get_assignment(assignment_id)
    if not assignment:
        return jsonify({"error": "not_found", "message": "Assignment not found"}), 404
    return jsonify({"data": assignment, "message": None}), 200

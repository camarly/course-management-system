"""
Forum routes.

Endpoints:
    POST  /api/courses/<course_id>/forums   Lecturer/admin creates a forum
    GET   /api/courses/<course_id>/forums   All forums for a course

Owner: Tramonique Wellington
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role
from app.services import forum_service

forums_bp = Blueprint('forums', __name__, url_prefix='/api')


@forums_bp.route("/courses/<int:course_id>/forums", methods=["POST"])
@require_role("lecturer", "admin")
def create_forum(course_id, current_user):
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    if not title:
        return jsonify({"error": "missing_fields", "message": "title is required"}), 400
    forum = forum_service.create_forum(
        course_id=course_id,
        title=title,
        description=body.get("description"),
        created_by=current_user["id"],
    )
    return jsonify({"data": forum, "message": "Forum created"}), 201


@forums_bp.route("/courses/<int:course_id>/forums", methods=["GET"])
@require_role("admin", "lecturer", "student")
def list_forums(course_id, current_user):
    forums = forum_service.list_forums(course_id)
    return jsonify({"data": forums, "message": None}), 200

"""
Thread routes.

Endpoints:
    POST  /api/forums/<forum_id>/threads    Create a new thread (title + opening post)
    GET   /api/forums/<forum_id>/threads    All threads in a forum
    GET   /api/threads/<thread_id>          Single thread with full nested reply tree

Owner: Tramonique Wellington
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role
from app.services import thread_service

threads_bp = Blueprint('threads', __name__, url_prefix='/api')


@threads_bp.route("/forums/<int:forum_id>/threads", methods=["POST"])
@require_role("admin", "lecturer", "student")
def create_thread(forum_id, current_user):
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    thread_body = body.get("body")
    if not title or not thread_body:
        return jsonify({"error": "missing_fields", "message": "title and body are required"}), 400
    thread = thread_service.create_thread(
        forum_id=forum_id,
        title=title,
        body=thread_body,
        created_by=current_user["id"],
    )
    return jsonify({"data": thread, "message": "Thread created"}), 201


@threads_bp.route("/forums/<int:forum_id>/threads", methods=["GET"])
@require_role("admin", "lecturer", "student")
def list_threads(forum_id, current_user):
    threads = thread_service.list_threads(forum_id)
    return jsonify({"data": threads, "message": None}), 200


@threads_bp.route("/threads/<int:thread_id>", methods=["GET"])
@require_role("admin", "lecturer", "student")
def get_thread(thread_id, current_user):
    thread = thread_service.get_thread_with_replies(thread_id)
    if not thread:
        return jsonify({"error": "not_found", "message": "Thread not found"}), 404
    return jsonify({"data": thread, "message": None}), 200

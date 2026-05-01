"""
Reply routes.

Endpoints:
    POST  /api/threads/<thread_id>/replies    Reply directly to a thread
    POST  /api/replies/<reply_id>/replies     Reply to a reply (nested, unlimited depth)

Owner: Tramonique Wellington
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role
from app.services import reply_service

replies_bp = Blueprint('replies', __name__, url_prefix='/api')


@replies_bp.route("/threads/<int:thread_id>/replies", methods=["POST"])
@require_role("admin", "lecturer", "student")
def reply_to_thread(thread_id, current_user):
    body = request.get_json(silent=True) or {}
    reply_body = body.get("body")
    if not reply_body:
        return jsonify({"error": "missing_fields", "message": "body is required"}), 400
    reply = reply_service.create_reply(
        thread_id=thread_id,
        body=reply_body,
        created_by=current_user["id"],
        parent_reply_id=None,
    )
    return jsonify({"data": reply, "message": "Reply posted"}), 201


@replies_bp.route("/replies/<int:reply_id>/replies", methods=["POST"])
@require_role("admin", "lecturer", "student")
def reply_to_reply(reply_id, current_user):
    body = request.get_json(silent=True) or {}
    reply_body = body.get("body")
    if not reply_body:
        return jsonify({"error": "missing_fields", "message": "body is required"}), 400
    # Look up the parent reply to get its thread_id
    from app.db.connection import get_connection
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT thread_id FROM replies WHERE id = %s", (reply_id,))
            parent = cur.fetchone()
    finally:
        conn.close()

    if not parent:
        return jsonify({"error": "not_found", "message": "Parent reply not found"}), 404

    reply = reply_service.create_reply(
        thread_id=parent["thread_id"],
        body=reply_body,
        created_by=current_user["id"],
        parent_reply_id=reply_id,
    )
    return jsonify({"data": reply, "message": "Reply posted"}), 201

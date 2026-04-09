"""
Reply routes.

Endpoints:
    POST  /api/threads/<thread_id>/replies    Reply directly to a thread
    POST  /api/replies/<reply_id>/replies     Reply to a reply (nested, unlimited depth)

The full reply tree is fetched via a recursive CTE.
parent_reply_id = NULL means a direct thread reply.
parent_reply_id = <id> means a reply to another reply.

Owner: Tramonique Wellington
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

replies_bp = Blueprint('replies', __name__, url_prefix='/api')

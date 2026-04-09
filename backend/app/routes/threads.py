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

threads_bp = Blueprint('threads', __name__, url_prefix='/api')

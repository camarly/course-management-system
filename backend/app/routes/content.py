"""
Course content routes.

Endpoints:
    POST  /api/courses/<course_id>/sections    Lecturer creates a content section
    GET   /api/courses/<course_id>/sections    All sections with nested content items
    POST  /api/sections/<section_id>/items     Lecturer adds a content item

Owner: Tamarica Shaw
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

content_bp = Blueprint('content', __name__, url_prefix='/api')

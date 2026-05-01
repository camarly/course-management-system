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
from app.services import content_service

content_bp = Blueprint('content', __name__, url_prefix='/api')


@content_bp.route("/courses/<int:course_id>/sections", methods=["POST"])
@require_role("lecturer")
def create_section(course_id, current_user):
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    if not title:
        return jsonify({"error": "missing_fields", "message": "title is required"}), 400
    section = content_service.create_section(
        course_id=course_id,
        title=title,
        position=body.get("position", 0),
    )
    return jsonify({"data": section, "message": "Section created"}), 201


@content_bp.route("/courses/<int:course_id>/sections", methods=["GET"])
@require_role("admin", "lecturer", "student")
def list_sections(course_id, current_user):
    sections = content_service.list_sections_with_items(course_id)
    return jsonify({"data": sections, "message": None}), 200


@content_bp.route("/sections/<int:section_id>/items", methods=["POST"])
@require_role("lecturer")
def add_item(section_id, current_user):
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    item_type = body.get("item_type")
    url = body.get("url")
    if not title or not item_type or not url:
        return jsonify({"error": "missing_fields", "message": "title, item_type, and url are required"}), 400
    item = content_service.add_item(
        section_id=section_id,
        title=title,
        item_type=item_type,
        url=url,
        position=body.get("position", 0),
    )
    return jsonify({"data": item, "message": "Item added"}), 201

"""
Calendar event routes.

Endpoints:
    POST  /api/courses/<course_id>/events          Create a calendar event
    GET   /api/courses/<course_id>/events          All events for a course
    GET   /api/students/<student_id>/events        Student events on a date (?date=YYYY-MM-DD)

Owner: Tamarica Shaw
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role
from app.services import calendar_service

calendar_bp = Blueprint('calendar', __name__, url_prefix='/api')


@calendar_bp.route("/courses/<int:course_id>/events", methods=["POST"])
@require_role("lecturer", "admin")
def create_event(course_id, current_user):
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    event_date = body.get("event_date")
    if not title or not event_date:
        return jsonify({"error": "missing_fields", "message": "title and event_date are required"}), 400
    event = calendar_service.create_event(
        course_id=course_id,
        title=title,
        description=body.get("description"),
        event_date=event_date,
        event_time=body.get("event_time"),
        created_by=current_user["id"],
    )
    return jsonify({"data": event, "message": "Event created"}), 201


@calendar_bp.route("/courses/<int:course_id>/events", methods=["GET"])
@require_role("admin", "lecturer", "student")
def list_events(course_id, current_user):
    events = calendar_service.list_events(course_id)
    return jsonify({"data": events, "message": None}), 200


@calendar_bp.route("/students/<int:student_id>/events", methods=["GET"])
@require_role("student", "admin")
def student_events(student_id, current_user):
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "missing_params", "message": "date query parameter required (?date=YYYY-MM-DD)"}), 400
    events = calendar_service.list_student_events_on_date(student_id, date)
    return jsonify({"data": events, "message": None}), 200

"""
User routes.

Endpoints:
    GET  /api/users/me      Return the currently authenticated user's profile
    GET  /api/users/:id     Admin: return any user by ID
    GET  /api/users         Admin: list all users

Owner: Camarly Thomas
"""

from flask import Blueprint, jsonify

from app.middleware.roles import require_role
from app.services import user_service

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/me", methods=["GET"])
@require_role("admin", "lecturer", "student")
def get_me(current_user):
    user = user_service.get_me(current_user["id"])
    if user is None:
        return jsonify({"error": "not_found", "message": "User not found"}), 404
    return jsonify({"data": user, "message": None}), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
@require_role("admin")
def get_user(user_id, current_user):
    user = user_service.get_by_id(user_id)
    if user is None:
        return jsonify({"error": "not_found", "message": "User not found"}), 404
    return jsonify({"data": user, "message": None}), 200


@users_bp.route("", methods=["GET"])
@users_bp.route("/", methods=["GET"])
@require_role("admin")
def list_users(current_user):
    users = user_service.get_all()
    return jsonify({"data": users, "message": None}), 200

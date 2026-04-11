"""
Authentication routes.

Endpoints:
    POST   /api/auth/register            Self-register (student or lecturer)
    POST   /api/auth/login               Login with username + password, returns JWT
    POST   /api/auth/admin/create-user   Admin creates an account for any user

JWT-only. No Google OAuth.

Owner: Camarly Thomas
"""

from flask import Blueprint, jsonify, request

from app.middleware.roles import require_role
from app.services import auth_service

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


_ERROR_STATUS = {
    "missing_fields": (400, "Missing required fields"),
    "invalid_role": (400, "Invalid role"),
    "duplicate": (409, "Username or email already taken"),
    "invalid_credentials": (401, "Invalid username or password"),
}


def _error(code: str):
    status, msg = _ERROR_STATUS.get(code, (400, code))
    return jsonify({"error": code, "message": msg}), status


@auth_bp.route("/register", methods=["POST"])
def register():
    body = request.get_json(silent=True) or {}
    try:
        user = auth_service.register(
            username=body.get("username"),
            email=body.get("email"),
            password=body.get("password"),
            role=body.get("role"),
        )
    except ValueError as exc:
        return _error(str(exc))
    return jsonify({"data": user, "message": "Registration successful"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    try:
        result = auth_service.login(
            username=body.get("username"),
            password=body.get("password"),
        )
    except ValueError as exc:
        return _error(str(exc))
    return jsonify({"data": result, "message": "Login successful"}), 200


@auth_bp.route("/admin/create-user", methods=["POST"])
@require_role("admin")
def admin_create_user(current_user):
    body = request.get_json(silent=True) or {}
    try:
        user = auth_service.admin_create_user(
            username=body.get("username"),
            email=body.get("email"),
            password=body.get("password"),
            role=body.get("role"),
        )
    except ValueError as exc:
        return _error(str(exc))
    return jsonify({"data": user, "message": "User created"}), 201

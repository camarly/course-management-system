"""
User routes.

Endpoints:
    GET  /api/users/me      Return the currently authenticated user's profile
    GET  /api/users/:id     Admin: return any user by ID
    GET  /api/users         Admin: list all users

Owner: Camarly Thomas
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

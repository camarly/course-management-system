"""
Authentication routes.

Endpoints:
    POST   /api/auth/register            Self-register (student or lecturer)
    POST   /api/auth/login               Login with username + password, returns JWT
    GET    /api/auth/google/login        Redirect to Google OAuth consent screen
    GET    /api/auth/google/callback     Handle OAuth callback, issue JWT
    POST   /api/auth/admin/create-user   Admin creates an account for any user

Owner: Camarly Thomas
"""

from flask import Blueprint, request, jsonify
from app.middleware.roles import require_role

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

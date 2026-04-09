"""
Role-based access control decorator.

Provides @require_role(*roles) — a Flask route decorator that:
  1. Calls get_current_user() to validate the JWT.
  2. Checks that the user's role is in the allowed list.
  3. Returns 403 JSON if the role is not permitted.
  4. Injects the current user payload into the wrapped function
     as the keyword argument `current_user`.

Usage:
    @require_role('admin', 'lecturer')
    def my_route(current_user):
        ...
"""

from functools import wraps
from flask import jsonify
from app.middleware.auth import get_current_user

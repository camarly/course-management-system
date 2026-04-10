"""
Role-based access control decorator.

Provides @require_role(*roles) -- a Flask route decorator that:
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

import logging
from functools import wraps
from flask import jsonify, g
from app.middleware.auth import get_current_user

logger = logging.getLogger(__name__)


def require_role(*roles):
    """Decorator that enforces JWT auth and role membership.

    Args:
        *roles: Allowed role strings (e.g. 'admin', 'lecturer', 'student').
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = get_current_user()

            # get_current_user returns a tuple (response, status) on failure
            if isinstance(result, tuple):
                return result

            if result["role"] not in roles:
                logger.debug("User %s has role '%s', needs one of %s",
                             result["id"], result["role"], roles)
                return jsonify({"error": "forbidden", "message": "Insufficient permissions"}), 403

            g.current_user = result
            kwargs["current_user"] = result
            return fn(*args, **kwargs)
        return wrapper
    return decorator

"""
JWT authentication middleware.

Provides get_current_user() which reads the Authorization: Bearer <token>
header, verifies the JWT signature, and returns the decoded payload as
{ 'id': int, 'role': str }.

Returns 401 JSON if the token is absent, expired, or invalid.
This function is imported by roles.py and can be used directly in routes.
"""

import logging

import jwt
from flask import request, jsonify
from app.config import JWT_SECRET

logger = logging.getLogger(__name__)


def get_current_user():
    """Extract and decode the JWT from the Authorization header.

    Returns:
        dict: {'id': int, 'role': str} on success.
        tuple: (JSON response, 401) on failure.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.debug("Missing or malformed Authorization header")
        return jsonify({"error": "unauthorized", "message": "Missing or invalid token"}), 401

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {"id": payload["sub"], "role": payload["role"]}
    except jwt.ExpiredSignatureError:
        logger.debug("Expired JWT")
        return jsonify({"error": "unauthorized", "message": "Token has expired"}), 401
    except jwt.InvalidTokenError as e:
        logger.debug("Invalid JWT: %s", e)
        return jsonify({"error": "unauthorized", "message": "Invalid token"}), 401

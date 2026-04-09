"""
JWT authentication middleware.

Provides get_current_user() which reads the Authorization: Bearer <token>
header, verifies the JWT signature, and returns the decoded payload as
{ 'id': int, 'role': str }.

Returns 401 JSON if the token is absent, expired, or invalid.
This function is imported by roles.py and can be used directly in routes.
"""

import os
from functools import wraps

import jwt
from flask import request, jsonify

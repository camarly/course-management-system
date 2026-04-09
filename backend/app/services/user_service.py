"""
User service.

Responsibilities:
    - Fetch the authenticated user's own profile
    - Fetch any user by ID (admin only)
    - List all users (admin only)

Owner: Camarly Thomas
"""

from app.db.connection import get_connection

"""
Authentication service.

Responsibilities:
    - Register a new user (hash password with bcrypt, INSERT into users)
    - Login: verify bcrypt hash, issue a signed JWT
    - Google OAuth: exchange auth code for id_token, UPSERT user, issue JWT
    - Admin create user: INSERT with a pre-set role

All queries use raw SQL via get_connection().

Owner: Camarly Thomas
"""

from app.db.connection import get_connection

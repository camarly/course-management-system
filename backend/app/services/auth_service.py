"""
Authentication service.

Responsibilities:
    - Register a new user (hash password with bcrypt, INSERT into users)
    - Login: verify bcrypt hash, issue a signed JWT
    - Admin create user: INSERT with a pre-set role (admin/lecturer/student)
    - create_token: sign JWTs used across the app

All queries use raw SQL via get_connection(). No ORM.
Every failure case raises ValueError — routes translate to HTTP codes.

Owner: Camarly Thomas
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import pymysql

from app.config import JWT_EXPIRY_HOURS, JWT_SECRET
from app.db.connection import get_connection

ALLOWED_SELF_ROLES = {"student", "lecturer"}
ALLOWED_ADMIN_ROLES = {"student", "lecturer", "admin"}


def create_token(user_id: int, role: str) -> str:
    """Sign a JWT with sub/role/exp claims and return it as a string."""
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))


def _insert_user(username: str, email: str, password: str, role: str) -> dict:
    password_hash = _hash_password(password)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO users (username, email, password_hash, role) "
                    "VALUES (%s, %s, %s, %s)",
                    (username, email, password_hash, role),
                )
            except pymysql.err.IntegrityError as exc:
                raise ValueError("duplicate") from exc
            conn.commit()
            new_id = cur.lastrowid
        return {"id": new_id, "username": username, "email": email, "role": role}
    finally:
        conn.close()


def register(username: str, email: str, password: str, role: str) -> dict:
    """Self-register a student or lecturer. Admin accounts must be created by an admin."""
    if not username or not email or not password or not role:
        raise ValueError("missing_fields")
    if role not in ALLOWED_SELF_ROLES:
        raise ValueError("invalid_role")
    return _insert_user(username, email, password, role)


def admin_create_user(username: str, email: str, password: str, role: str) -> dict:
    """Admin-only: create an account for any role, including admin."""
    if not username or not email or not password or not role:
        raise ValueError("missing_fields")
    if role not in ALLOWED_ADMIN_ROLES:
        raise ValueError("invalid_role")
    return _insert_user(username, email, password, role)


def login(username: str, password: str) -> dict:
    """Verify credentials and return a fresh JWT plus a sanitised user dict."""
    if not username or not password:
        raise ValueError("missing_fields")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, password_hash, role "
                "FROM users WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row or not _verify_password(password, row["password_hash"]):
        raise ValueError("invalid_credentials")

    token = create_token(row["id"], row["role"])
    return {
        "token": token,
        "user": {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "role": row["role"],
        },
    }

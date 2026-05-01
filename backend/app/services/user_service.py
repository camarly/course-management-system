"""
User service.

Responsibilities:
    - Fetch the authenticated user's own profile
    - Fetch any user by ID (admin only)
    - List all users (admin only)

Never returns password_hash.

Owner: Camarly Thomas
"""

from app.db.connection import get_connection

_USER_COLS = "id, username, email, role, created_at"


def get_me(user_id: int) -> dict | None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {_USER_COLS} FROM users WHERE id = %s",
                (user_id,),
            )
            return cur.fetchone()
    finally:
        conn.close()


def get_by_id(user_id: int) -> dict | None:
    return get_me(user_id)


def get_all() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {_USER_COLS} FROM users ORDER BY id")
            return cur.fetchall()
    finally:
        conn.close()

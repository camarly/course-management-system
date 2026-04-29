"""
User seeding module.

Generates and bulk-inserts:
    - >= 100,000 students
    - Enough lecturers to cover all 200+ courses (max 5 courses each)
    - At least 1 admin account

Uses Faker for realistic usernames and emails.
Passwords are bcrypt-hashed.
Inserts in batches of 1,000 rows per query.

Owner: Camarly Thomas
"""

import bcrypt
from faker import Faker

from app.db.connection import get_connection

fake = Faker()

# Pre-hash a single password for all seeded users (speed over realism)
_SEED_PASSWORD_HASH = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode("utf-8")

BATCH_SIZE = 1000


def seed_admin(conn):
    """Insert the default admin account. Returns admin user id."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT IGNORE INTO users (username, email, password_hash, role) "
            "VALUES (%s, %s, %s, %s)",
            ("admin", "admin@lms.local", _SEED_PASSWORD_HASH, "admin"),
        )
        conn.commit()
        cur.execute("SELECT id FROM users WHERE username = 'admin'")
        return cur.fetchone()["id"]


def seed_lecturers(conn, count=50):
    """Insert lecturer accounts. Returns list of lecturer IDs."""
    ids = []
    rows = []
    for i in range(count):
        username = f"lecturer_{i}"
        email = f"lecturer_{i}@lms.local"
        rows.append((username, email, _SEED_PASSWORD_HASH, "lecturer"))
        if len(rows) >= BATCH_SIZE:
            _insert_batch(conn, rows)
            rows = []
    if rows:
        _insert_batch(conn, rows)

    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE role = 'lecturer' ORDER BY id")
        ids = [r["id"] for r in cur.fetchall()]
    return ids


def seed_students(conn, count=100_000):
    """Insert student accounts. Returns list of student IDs."""
    rows = []
    for i in range(count):
        username = f"student_{i}"
        email = f"student_{i}@lms.local"
        rows.append((username, email, _SEED_PASSWORD_HASH, "student"))
        if len(rows) >= BATCH_SIZE:
            _insert_batch(conn, rows)
            rows = []
    if rows:
        _insert_batch(conn, rows)

    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE role = 'student' ORDER BY id")
        ids = [r["id"] for r in cur.fetchall()]
    return ids


def _insert_batch(conn, rows):
    """Batch-insert user rows."""
    placeholders = ", ".join(["(%s, %s, %s, %s)"] * len(rows))
    flat = []
    for r in rows:
        flat.extend(r)
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT IGNORE INTO users (username, email, password_hash, role) "
            f"VALUES {placeholders}",
            tuple(flat),
        )
    conn.commit()

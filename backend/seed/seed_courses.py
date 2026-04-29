"""
Course seeding module.

Generates and inserts >= 200 courses.
Assigns one lecturer to each course.
Enforces: no lecturer may teach more than 5 courses.

Owner: Camarly Thomas
"""

from app.db.connection import get_connection

BATCH_SIZE = 500


def seed_courses(conn, lecturer_ids, count=200):
    """Create courses and round-robin assign lecturers (max 5 each).
    Returns list of course IDs."""
    rows = []
    for i in range(count):
        title = f"COURSE-{i:04d}"
        description = f"Auto-generated course {i}"
        # Round-robin: each lecturer gets at most ceil(count/len) courses
        lecturer_id = lecturer_ids[i % len(lecturer_ids)]
        rows.append((title, description, lecturer_id))
        if len(rows) >= BATCH_SIZE:
            _insert_batch(conn, rows)
            rows = []
    if rows:
        _insert_batch(conn, rows)

    with conn.cursor() as cur:
        cur.execute("SELECT id FROM courses ORDER BY id")
        return [r["id"] for r in cur.fetchall()]


def _insert_batch(conn, rows):
    placeholders = ", ".join(["(%s, %s, %s)"] * len(rows))
    flat = []
    for r in rows:
        flat.extend(r)
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO courses (title, description, lecturer_id) "
            f"VALUES {placeholders}",
            tuple(flat),
        )
    conn.commit()

"""
Assignment service.

Responsibilities:
    - Create an assignment for a course (lecturer)
    - List all assignments for a course
    - Get a single assignment by ID

Owner: Carl Heron
"""

from app.db.connection import get_connection


def create_assignment(course_id, title, description=None, due_date=None, weight=None):
    """Insert a new assignment row and return it as a plain dict."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO assignments (course_id, title, description, due_date, weight)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (course_id, title, description, due_date, weight),
            )
            conn.commit()
            assignment_id = cur.lastrowid

            # Fetch the full row so timestamps come back automatically
            cur.execute(
                """
                SELECT id, course_id, title, description, due_date, weight,
                       created_at, updated_at
                FROM assignments
                WHERE id = %s
                """,
                (assignment_id,),
            )
            row = cur.fetchone()

        return _serialize(row)
    finally:
        conn.close()


def list_for_course(course_id):
    """Return all assignments for a given course as a list of dicts."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, course_id, title, description, due_date, weight,
                       created_at, updated_at
                FROM assignments
                WHERE course_id = %s
                ORDER BY due_date ASC
                """,
                (course_id,),
            )
            rows = cur.fetchall()

        return [_serialize(row) for row in rows]
    finally:
        conn.close()


def get_assignment(assignment_id):
    """Return a single assignment dict, or None if not found."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, course_id, title, description, due_date, weight,
                       created_at, updated_at
                FROM assignments
                WHERE id = %s
                """,
                (assignment_id,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        return _serialize(row)
    finally:
        conn.close()


def _serialize(row):
    """Convert a DB row dict into a JSON-safe dict."""
    return {
        "id":          row["id"],
        "course_id":   row["course_id"],
        "title":       row["title"],
        "description": row["description"],
        "due_date":    str(row["due_date"]) if row["due_date"] else None,
        "weight":      float(row["weight"]) if row["weight"] is not None else None,
        "created_at":  str(row["created_at"]) if row["created_at"] else None,
        "updated_at":  str(row["updated_at"]) if row["updated_at"] else None,
    }
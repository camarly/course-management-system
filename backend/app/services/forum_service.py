"""
Forum service.

Responsibilities:
    - Create a forum for a course (lecturer / admin)
    - List all forums belonging to a course

Owner: Tramonique Wellington
"""

from app.db.connection import get_connection


def create_forum(course_id, title, description=None, created_by=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO forums (course_id, title, description, created_by) "
                "VALUES (%s, %s, %s, %s)",
                (course_id, title, description, created_by),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "course_id": course_id,
            "title": title,
            "description": description,
            "created_by": created_by,
        }
    finally:
        conn.close()


def list_forums(course_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, course_id, title, description, created_by, created_at "
                "FROM forums WHERE course_id = %s "
                "ORDER BY created_at DESC",
                (course_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()

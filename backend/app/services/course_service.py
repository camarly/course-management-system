"""
Course service.

Responsibilities:
    - Create a course (admin)
    - List all courses
    - Get a single course by ID
    - Get all members of a course (students + lecturer)
    - Assign a lecturer to a course — enforces one-lecturer rule and
      the 5-course lecturer cap; replaces any existing assignment
    - Get all courses for a specific student
    - Get all courses for a specific lecturer

Owner: Tamarica Shaw
"""

from app.db.connection import get_connection


def create_course(title, description, lecturer_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO courses (title, description, lecturer_id) "
                "VALUES (%s, %s, %s)",
                (title, description, lecturer_id),
            )
            course_id = cur.lastrowid
            conn.commit()

            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at, updated_at "
                "FROM courses WHERE id = %s",
                (course_id,),
            )
            return cur.fetchone()
    finally:
        conn.close()


def list_courses():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at "
                "FROM courses ORDER BY id"
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_course(course_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at "
                "FROM courses WHERE id = %s",
                (course_id,),
            )
            return cur.fetchone()
    finally:
        conn.close()

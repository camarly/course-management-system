"""
Assignment service.

Responsibilities:
    - Create an assignment for a course (lecturer)
    - List all assignments for a course
    - Get a single assignment by ID

Owner: Carl Heron
"""

from app.db.connection import get_connection


def create_assignment(course_id, title, due_date, weight, description=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO assignments (course_id, title, description, due_date, weight) "
                "VALUES (%s, %s, %s, %s, %s)",
                (course_id, title, description, due_date, weight),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "course_id": course_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "weight": float(weight),
        }
    finally:
        conn.close()


def list_for_course(course_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, course_id, title, description, due_date, weight, created_at "
                "FROM assignments WHERE course_id = %s "
                "ORDER BY due_date",
                (course_id,),
            )
            rows = cur.fetchall()
            for row in rows:
                if row.get("weight") is not None:
                    row["weight"] = float(row["weight"])
            return rows
    finally:
        conn.close()


def get_assignment(assignment_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, course_id, title, description, due_date, weight, created_at "
                "FROM assignments WHERE id = %s",
                (assignment_id,),
            )
            row = cur.fetchone()
            if row and row.get("weight") is not None:
                row["weight"] = float(row["weight"])
            return row
    finally:
        conn.close()

"""
Enrollment service.

Responsibilities:
    - Enroll a student in a course
    - Enforce 6-course cap per student (raise 403 if exceeded)
    - Detect and reject duplicate enrollments (raise 409)
    - Verify the course exists before enrolling (raise 404)

Owner: Tamarica Shaw
"""

import pymysql

from app.db.connection import get_connection


def enroll(student_id, course_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Verify course exists
            cur.execute("SELECT id FROM courses WHERE id = %s", (course_id,))
            if not cur.fetchone():
                raise ValueError("course_not_found")

            # Enforce 6-course cap
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM enrollments WHERE student_id = %s",
                (student_id,),
            )
            if cur.fetchone()["cnt"] >= 6:
                raise ValueError("enrollment_limit")

            # Insert (UNIQUE constraint catches duplicates)
            try:
                cur.execute(
                    "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)",
                    (student_id, course_id),
                )
            except pymysql.err.IntegrityError:
                raise ValueError("duplicate_enrollment")

            conn.commit()
            new_id = cur.lastrowid
            return {
                "id": new_id,
                "student_id": student_id,
                "course_id": course_id,
            }
    finally:
        conn.close()

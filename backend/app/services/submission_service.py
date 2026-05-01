"""
Submission service.

Responsibilities:
    - Submit an assignment (student) -- enforce one submission per student per assignment
    - List all submissions for an assignment (lecturer / admin)
    - List all grades for a student (joins submissions -> grades)

Owner: Carl Heron
"""

import pymysql

from app.db.connection import get_connection


def submit(assignment_id, student_id, file_url):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO submissions (assignment_id, student_id, file_url) "
                    "VALUES (%s, %s, %s)",
                    (assignment_id, student_id, file_url),
                )
            except pymysql.err.IntegrityError:
                raise ValueError("duplicate_submission")
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "assignment_id": assignment_id,
            "student_id": student_id,
            "file_url": file_url,
        }
    finally:
        conn.close()


def list_submissions(assignment_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT s.id, s.assignment_id, s.student_id, s.file_url, s.submitted_at, "
                "u.username AS student_username "
                "FROM submissions s "
                "JOIN users u ON u.id = s.student_id "
                "WHERE s.assignment_id = %s "
                "ORDER BY s.submitted_at",
                (assignment_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()


def list_student_grades(student_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT g.id AS grade_id, g.score, g.feedback, g.graded_at, "
                "s.id AS submission_id, s.assignment_id, s.file_url, "
                "a.title AS assignment_title, a.course_id, a.weight "
                "FROM grades g "
                "JOIN submissions s ON s.id = g.submission_id "
                "JOIN assignments a ON a.id = s.assignment_id "
                "WHERE s.student_id = %s "
                "ORDER BY g.graded_at",
                (student_id,),
            )
            rows = cur.fetchall()
            for row in rows:
                if row.get("score") is not None:
                    row["score"] = float(row["score"])
                if row.get("weight") is not None:
                    row["weight"] = float(row["weight"])
            return rows
    finally:
        conn.close()

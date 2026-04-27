"""
Grade service.

Responsibilities:
    - Record a grade for a submission (lecturer)
    - After writing the grade, enqueue the grade_tasks.recalculate_average
      Celery task for the student

Owner: Carl Heron
"""

import pymysql

from app.db.connection import get_connection


def record_grade(submission_id, graded_by, score, feedback=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Get the student_id from the submission
            cur.execute(
                "SELECT student_id FROM submissions WHERE id = %s",
                (submission_id,),
            )
            submission = cur.fetchone()
            if not submission:
                raise ValueError("submission_not_found")

            # Insert grade (UNIQUE on submission_id prevents double grading)
            try:
                cur.execute(
                    "INSERT INTO grades (submission_id, graded_by, score, feedback) "
                    "VALUES (%s, %s, %s, %s)",
                    (submission_id, graded_by, score, feedback),
                )
            except pymysql.err.IntegrityError:
                raise ValueError("already_graded")

            conn.commit()
            new_id = cur.lastrowid

        # Enqueue async grade recalculation
        try:
            from app.tasks.grade_tasks import recalculate_average
            recalculate_average.delay(submission["student_id"])
        except Exception:
            pass  # Celery failure is non-fatal

        return {
            "id": new_id,
            "submission_id": submission_id,
            "graded_by": graded_by,
            "score": float(score),
            "feedback": feedback,
        }
    finally:
        conn.close()

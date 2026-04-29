"""
Grade recalculation Celery tasks.

Tasks:
    recalculate_average(student_id)
        Fetches all grades for the student across all submissions,
        computes the weighted average using assignment weights,
        and upserts the result into student_averages.

This task is enqueued by grade_service after every grade write.

Owner: Camarly Thomas
"""

from app.tasks.celery_app import celery_app
from app.db.connection import get_connection


@celery_app.task(name="grade_tasks.recalculate_average")
def recalculate_average(student_id):
    """Compute the weighted average grade for a student and upsert into student_averages."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Fetch all grades with their assignment weights
            cur.execute(
                "SELECT g.score, a.weight "
                "FROM grades g "
                "JOIN submissions s ON s.id = g.submission_id "
                "JOIN assignments a ON a.id = s.assignment_id "
                "WHERE s.student_id = %s",
                (student_id,),
            )
            rows = cur.fetchall()

            if not rows:
                return

            total_weighted = sum(float(r["score"]) * float(r["weight"]) for r in rows)
            total_weight = sum(float(r["weight"]) for r in rows)

            if total_weight == 0:
                return

            average = total_weighted / total_weight

            # Upsert into student_averages
            cur.execute(
                "INSERT INTO student_averages (student_id, average_grade) "
                "VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE average_grade = %s, last_updated = NOW()",
                (student_id, average, average),
            )
            conn.commit()
    finally:
        conn.close()

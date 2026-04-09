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

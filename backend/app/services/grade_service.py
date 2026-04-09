"""
Grade service.

Responsibilities:
    - Record a grade for a submission (lecturer)
    - After writing the grade, enqueue the grade_tasks.recalculate_average
      Celery task for the student

Owner: Carl Heron
"""

from app.db.connection import get_connection

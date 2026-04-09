"""
Submission service.

Responsibilities:
    - Submit an assignment (student) — enforce one submission per student per assignment
    - List all submissions for an assignment (lecturer / admin)
    - List all grades for a student (joins submissions → grades)

After a submission is created, the grade_tasks.recalculate_average
Celery task should NOT be triggered here (no grade exists yet).
The task is triggered from grade_service after a grade is written.

Owner: Carl Heron
"""

from app.db.connection import get_connection

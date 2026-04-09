"""
Enrollment service.

Responsibilities:
    - Enroll a student in a course
    - Enforce 6-course cap per student (raise 403 if exceeded)
    - Detect and reject duplicate enrollments (raise 409)
    - Verify the course exists before enrolling (raise 404)

Owner: Tamarica Shaw
"""

from app.db.connection import get_connection

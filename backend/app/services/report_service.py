"""
Report service.

Responsibilities:
    - Query each of the five report views defined in migration 014:
        vw_courses_50_plus
        vw_students_5_plus_courses
        vw_lecturers_3_plus_courses
        vw_top10_enrolled_courses
        vw_top10_students_by_average

All report queries are SELECT * FROM <view_name> — no business logic.
Results are cached in Redis by the route handler using cache helpers.

Owner: Carl Heron
"""

from app.db.connection import get_connection

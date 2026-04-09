"""
Enrollment seeding module.

Enrolls students into courses satisfying all spec constraints:
    - Every student is enrolled in >= 3 courses (max 6)
    - Every course has >= 10 enrolled students

Uses a two-pass strategy:
    Pass 1 — ensure every course reaches the 10-student minimum.
    Pass 2 — assign remaining enrollment slots to students
              until every student meets the 3-course minimum.

Owner: Camarly Thomas
"""

from app.db.connection import get_connection

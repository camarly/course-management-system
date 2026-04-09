"""
Course seeding module.

Generates and inserts >= 200 courses.
Assigns one lecturer to each course.
Enforces: no lecturer may teach more than 5 courses.

Owner: Camarly Thomas
"""

from app.db.connection import get_connection

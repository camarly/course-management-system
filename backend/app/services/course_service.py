"""
Course service.

Responsibilities:
    - Create a course (admin)
    - List all courses
    - Get a single course by ID
    - Get all members of a course (students + lecturer)
    - Assign a lecturer to a course — enforces one-lecturer rule and
      the 5-course lecturer cap; replaces any existing assignment
    - Get all courses for a specific student
    - Get all courses for a specific lecturer

Owner: Tamarica Shaw
"""

from app.db.connection import get_connection

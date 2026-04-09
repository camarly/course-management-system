"""
Seeding Celery tasks.

Tasks:
    seed_all()          Orchestrates the full seed run in order.
    seed_users()        Bulk-inserts 100,000+ students and required lecturers/admins.
    seed_courses()      Bulk-inserts 200+ courses and assigns lecturers.
    seed_enrollments()  Enrols students: each student >= 3 courses,
                        each course >= 10 members, no student > 6 courses.
    seed_assignments()  Creates assignments and grades for seeded courses.

Uses chunked batch INSERT statements — not one query per row.

Owner: Camarly Thomas
"""

from app.tasks.celery_app import celery_app
from app.db.connection import get_connection

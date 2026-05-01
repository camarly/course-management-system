"""
Seed runner entry point.

Calls each seed module in dependency order:
    1. seed_users      -- create students, lecturers, admin
    2. seed_courses    -- create courses, assign lecturers
    3. seed_enrollments -- enrol students, enforce spec constraints
    4. seed_assignments -- create assignments and sample grades

Run directly:
    python -m seed.seed_runner

Or trigger via Celery:
    from app.tasks.seed_tasks import seed_all
    seed_all.delay()

Owner: Camarly Thomas
"""

import time

from app.db.connection import get_connection
from seed.seed_users import seed_admin, seed_lecturers, seed_students
from seed.seed_courses import seed_courses
from seed.seed_enrollments import seed_enrollments
from seed.seed_assignments import seed_assignments, seed_submissions_and_grades


def run_seed():
    """Execute the full seed pipeline."""
    conn = get_connection()
    try:
        print("=== LMS Seed Runner ===")

        t0 = time.time()
        print("[1/6] Creating admin...")
        admin_id = seed_admin(conn)
        print(f"       Admin ID: {admin_id}")

        print("[2/6] Creating lecturers...")
        lecturer_ids = seed_lecturers(conn, count=50)
        print(f"       Lecturers: {len(lecturer_ids)}")

        print("[3/6] Creating students (100,000)...")
        student_ids = seed_students(conn, count=100_000)
        print(f"       Students: {len(student_ids)}")

        print("[4/6] Creating courses (200)...")
        course_ids = seed_courses(conn, lecturer_ids, count=200)
        print(f"       Courses: {len(course_ids)}")

        print("[5/6] Creating enrollments...")
        total_enrollments = seed_enrollments(conn, student_ids, course_ids)
        print(f"       Enrollments: {total_enrollments}")

        print("[6/6] Creating assignments, submissions, grades...")
        assignments_by_course = seed_assignments(conn, course_ids)
        seed_submissions_and_grades(conn, assignments_by_course)

        elapsed = time.time() - t0
        print(f"=== Seed complete in {elapsed:.1f}s ===")
    finally:
        conn.close()


if __name__ == "__main__":
    run_seed()

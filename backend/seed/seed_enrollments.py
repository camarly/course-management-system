"""
Enrollment seeding module.

Enrolls students into courses satisfying all spec constraints:
    - Every student is enrolled in >= 3 courses (max 6)
    - Every course has >= 10 enrolled students

Uses a two-pass strategy:
    Pass 1 -- ensure every course reaches the 10-student minimum.
    Pass 2 -- assign remaining enrollment slots to students
              until every student meets the 3-course minimum.

Owner: Camarly Thomas
"""

import random

from app.db.connection import get_connection

BATCH_SIZE = 1000
MIN_PER_COURSE = 10
MIN_PER_STUDENT = 3
MAX_PER_STUDENT = 6


def seed_enrollments(conn, student_ids, course_ids):
    """Two-pass enrollment seeding. Returns total enrollment count."""
    random.seed(42)  # reproducible

    # Track state
    student_courses = {sid: set() for sid in student_ids}
    course_students = {cid: set() for cid in course_ids}

    # Pass 1: ensure every course has at least MIN_PER_COURSE students
    for cid in course_ids:
        eligible = [
            sid for sid in student_ids
            if len(student_courses[sid]) < MAX_PER_STUDENT and cid not in student_courses[sid]
        ]
        need = MIN_PER_COURSE - len(course_students[cid])
        if need > 0:
            chosen = random.sample(eligible, min(need, len(eligible)))
            for sid in chosen:
                student_courses[sid].add(cid)
                course_students[cid].add(sid)

    # Pass 2: ensure every student has at least MIN_PER_STUDENT courses
    for sid in student_ids:
        need = MIN_PER_STUDENT - len(student_courses[sid])
        if need > 0:
            eligible = [
                cid for cid in course_ids
                if cid not in student_courses[sid]
            ]
            chosen = random.sample(eligible, min(need, len(eligible)))
            for cid in chosen:
                student_courses[sid].add(cid)
                course_students[cid].add(sid)

    # Batch insert all enrollments
    rows = []
    total = 0
    for sid, courses in student_courses.items():
        for cid in courses:
            rows.append((sid, cid))
            if len(rows) >= BATCH_SIZE:
                _insert_batch(conn, rows)
                total += len(rows)
                rows = []
    if rows:
        _insert_batch(conn, rows)
        total += len(rows)

    return total


def _insert_batch(conn, rows):
    placeholders = ", ".join(["(%s, %s)"] * len(rows))
    flat = []
    for r in rows:
        flat.extend(r)
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT IGNORE INTO enrollments (student_id, course_id) "
            f"VALUES {placeholders}",
            tuple(flat),
        )
    conn.commit()

"""
Assignment and grade seeding module.

For each seeded course:
    - Creates 2-4 sample assignments with randomised weights summing to 100.
    - Creates sample submissions for enrolled students.
    - Creates sample grades and triggers average recalculation.

Owner: Camarly Thomas
"""

import random
from datetime import datetime, timedelta

from app.db.connection import get_connection

BATCH_SIZE = 1000


def seed_assignments(conn, course_ids):
    """Create assignments for each course. Returns mapping of course_id -> [assignment rows]."""
    random.seed(99)
    all_assignments = {}
    rows = []

    for cid in course_ids:
        num = random.randint(2, 4)
        weights = _random_weights(num)
        course_assignments = []
        for i in range(num):
            title = f"Assignment {i + 1}"
            description = f"Auto-generated assignment {i + 1} for course {cid}"
            due_date = (datetime.now() + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d %H:%M:%S")
            rows.append((cid, title, description, due_date, weights[i]))
            course_assignments.append({"weight": weights[i]})

        all_assignments[cid] = course_assignments

        if len(rows) >= BATCH_SIZE:
            _insert_assignment_batch(conn, rows)
            rows = []

    if rows:
        _insert_assignment_batch(conn, rows)

    # Fetch all assignment IDs grouped by course
    result = {}
    with conn.cursor() as cur:
        cur.execute("SELECT id, course_id, weight FROM assignments ORDER BY id")
        for row in cur.fetchall():
            result.setdefault(row["course_id"], []).append(row)
    return result


def seed_submissions_and_grades(conn, assignments_by_course):
    """For a sample of students per course, create submissions and grades."""
    random.seed(123)

    with conn.cursor() as cur:
        for course_id, assignments in assignments_by_course.items():
            # Get enrolled students for this course (sample up to 20)
            cur.execute(
                "SELECT student_id FROM enrollments WHERE course_id = %s",
                (course_id,),
            )
            enrolled = [r["student_id"] for r in cur.fetchall()]
            sample = enrolled[:min(20, len(enrolled))]

            for assignment in assignments:
                aid = assignment["id"]
                sub_rows = []
                for sid in sample:
                    sub_rows.append((aid, sid, f"https://files.lms.local/{aid}/{sid}.pdf"))

                if sub_rows:
                    _insert_submission_batch(conn, sub_rows)

            # Fetch submission IDs for grading
            for assignment in assignments:
                aid = assignment["id"]
                cur.execute(
                    "SELECT id, student_id FROM submissions WHERE assignment_id = %s",
                    (aid,),
                )
                subs = cur.fetchall()
                grade_rows = []
                for sub in subs:
                    score = round(random.uniform(40, 100), 2)
                    grade_rows.append((sub["id"], 1, score, None))  # graded_by=1 (admin)
                if grade_rows:
                    _insert_grade_batch(conn, grade_rows)

    conn.commit()


def _random_weights(n):
    """Generate n random weights that sum to 100."""
    points = sorted(random.sample(range(1, 100), n - 1))
    weights = []
    prev = 0
    for p in points:
        weights.append(p - prev)
        prev = p
    weights.append(100 - prev)
    return weights


def _insert_assignment_batch(conn, rows):
    placeholders = ", ".join(["(%s, %s, %s, %s, %s)"] * len(rows))
    flat = []
    for r in rows:
        flat.extend(r)
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO assignments (course_id, title, description, due_date, weight) "
            f"VALUES {placeholders}",
            tuple(flat),
        )
    conn.commit()


def _insert_submission_batch(conn, rows):
    placeholders = ", ".join(["(%s, %s, %s)"] * len(rows))
    flat = []
    for r in rows:
        flat.extend(r)
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT IGNORE INTO submissions (assignment_id, student_id, file_url) "
            f"VALUES {placeholders}",
            tuple(flat),
        )
    conn.commit()


def _insert_grade_batch(conn, rows):
    placeholders = ", ".join(["(%s, %s, %s, %s)"] * len(rows))
    flat = []
    for r in rows:
        flat.extend(r)
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT IGNORE INTO grades (submission_id, graded_by, score, feedback) "
            f"VALUES {placeholders}",
            tuple(flat),
        )
    conn.commit()

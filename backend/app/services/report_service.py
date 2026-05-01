"""
Report service.

Responsibilities:
    - Query each of the five report views defined in migration 014:
        vw_courses_50_plus
        vw_students_5_plus_courses
        vw_lecturers_3_plus_courses
        vw_top10_enrolled_courses
        vw_top10_students_by_average

All report queries are SELECT * FROM <view_name> -- no business logic.
Results are cached in Redis by the route handler using cache helpers.

Owner: Carl Heron
"""

from app.db.connection import get_connection


def courses_50_plus():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vw_courses_50_plus")
            return cur.fetchall()
    finally:
        conn.close()


def students_5_plus_courses():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vw_students_5_plus_courses")
            return cur.fetchall()
    finally:
        conn.close()


def lecturers_3_plus_courses():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vw_lecturers_3_plus_courses")
            return cur.fetchall()
    finally:
        conn.close()


def top10_enrolled_courses():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vw_top10_enrolled_courses")
            return cur.fetchall()
    finally:
        conn.close()


def top10_students_by_average():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vw_top10_students_by_average")
            rows = cur.fetchall()
            for row in rows:
                if row.get("average_grade") is not None:
                    row["average_grade"] = float(row["average_grade"])
            return rows
    finally:
        conn.close()

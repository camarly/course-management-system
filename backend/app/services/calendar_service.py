"""
Calendar event service.

Responsibilities:
    - Create a calendar event for a course
    - List all calendar events for a course
    - List all calendar events for a specific student on a given date
      (joins enrollments -> calendar_events WHERE event_date = :date)

Owner: Tamarica Shaw
"""

from app.db.connection import get_connection


def create_event(course_id, title, description, event_date, event_time, created_by):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO calendar_events "
                "(course_id, title, description, event_date, event_time, created_by) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (course_id, title, description, event_date, event_time, created_by),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "course_id": course_id,
            "title": title,
            "description": description,
            "event_date": event_date,
            "event_time": event_time,
            "created_by": created_by,
        }
    finally:
        conn.close()


def list_events(course_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, course_id, title, description, event_date, "
                "event_time, created_by, created_at "
                "FROM calendar_events WHERE course_id = %s "
                "ORDER BY event_date, event_time",
                (course_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()


def list_student_events_on_date(student_id, date):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ce.id, ce.course_id, ce.title, ce.description, "
                "ce.event_date, ce.event_time, ce.created_by, ce.created_at "
                "FROM calendar_events ce "
                "JOIN enrollments e ON e.course_id = ce.course_id "
                "WHERE e.student_id = %s AND ce.event_date = %s "
                "ORDER BY ce.event_time",
                (student_id, date),
            )
            return cur.fetchall()
    finally:
        conn.close()

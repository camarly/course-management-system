"""
Calendar event service.

Responsibilities:
    - Create a calendar event for a course
    - List all calendar events for a course
    - List all calendar events for a specific student on a given date
      (joins enrollments → calendar_events WHERE event_date = :date)

Owner: Tamarica Shaw
"""

from app.db.connection import get_connection

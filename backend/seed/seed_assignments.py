"""
Assignment and grade seeding module.

For each seeded course:
    - Creates 2–4 sample assignments with randomised weights summing to 100.
    - Creates sample submissions for enrolled students.
    - Creates sample grades and triggers average recalculation.

Owner: Camarly Thomas
"""

from app.db.connection import get_connection

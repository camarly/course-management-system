"""
User seeding module.

Generates and bulk-inserts:
    - >= 100,000 students
    - Enough lecturers to cover all 200+ courses (max 5 courses each)
    - At least 1 admin account

Uses Faker for realistic usernames and emails.
Passwords are bcrypt-hashed.
Inserts in batches of 1,000 rows per query.

Owner: Camarly Thomas
"""

from app.db.connection import get_connection

"""
Seed package.

Run seed_runner.py directly or invoke seed_all() via Celery
to populate the database with the minimum required data:
    - >= 100,000 students
    - >= 200 courses
    - Every student enrolled in >= 3 courses (max 6)
    - Every course with >= 10 enrolled students
    - Every lecturer assigned >= 1 course (max 5)
"""

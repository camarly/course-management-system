"""
Seed runner entry point.

Calls each seed module in dependency order:
    1. seed_users      — create students, lecturers, admin
    2. seed_courses    — create courses, assign lecturers
    3. seed_enrollments — enrol students, enforce spec constraints
    4. seed_assignments — create assignments and sample grades

Run directly:
    python -m seed.seed_runner

Or trigger via Celery:
    from app.tasks.seed_tasks import seed_all
    seed_all.delay()

Owner: Camarly Thomas
"""

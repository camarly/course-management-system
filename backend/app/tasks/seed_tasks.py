"""
Seeding Celery tasks.

Tasks:
    seed_all()          Orchestrates the full seed run in order.

Uses chunked batch INSERT statements -- not one query per row.

Owner: Camarly Thomas
"""

from app.tasks.celery_app import celery_app


@celery_app.task(name="seed_tasks.seed_all")
def seed_all():
    """Run the full seed pipeline as an async Celery task."""
    from seed.seed_runner import run_seed
    run_seed()

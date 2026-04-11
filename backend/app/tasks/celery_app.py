"""
Celery application instance.

Configures Celery to use Redis as both the broker and result backend.
Broker uses CELERY_BROKER_URL (redis db 1).
Result backend uses CELERY_RESULT_BACKEND (redis db 2).

Import `celery_app` from this module wherever a task needs to be defined
or enqueued:
    from app.tasks.celery_app import celery_app

Owner: Camarly Thomas
"""

from celery import Celery

from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "lms",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.autodiscover_tasks(["app.tasks"])


@celery_app.task(name="app.tasks.ping")
def ping() -> str:
    """Smoke-test task used to verify the worker is consuming from Redis."""
    return "pong"

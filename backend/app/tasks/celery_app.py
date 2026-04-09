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

import os
from celery import Celery

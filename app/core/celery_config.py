"""
Celery configuration for background tasks
"""
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "pharmacy_audit_platform",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=['app.workers.celery_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
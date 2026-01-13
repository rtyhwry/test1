"""
Celery application configuration
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ev_test_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.task_executor",
        "app.workers.upgrade_worker",
        "app.workers.report_generator",
        "app.workers.sync_worker",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.MAX_TASK_TIMEOUT,
    task_soft_time_limit=settings.DEFAULT_TASK_TIMEOUT,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Task routes
    task_routes={
        "app.workers.task_executor.*": {"queue": "task_queue"},
        "app.workers.upgrade_worker.*": {"queue": "upgrade_queue"},
        "app.workers.report_generator.*": {"queue": "report_queue"},
        "app.workers.sync_worker.*": {"queue": "sync_queue"},
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "check-scheduled-tasks": {
            "task": "app.workers.task_executor.check_scheduled_tasks",
            "schedule": 60.0,  # Every minute
        },
        "cleanup-old-logs": {
            "task": "app.workers.task_executor.cleanup_old_logs",
            "schedule": 86400.0,  # Daily
        },
        "sync-alm-tasks": {
            "task": "app.workers.sync_worker.sync_alm_tasks",
            "schedule": 3600.0,  # Hourly
        },
    }
)

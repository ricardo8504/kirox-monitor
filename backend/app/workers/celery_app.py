from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "odoo_monitor",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "collect-all-servers": {
            "task": "app.workers.tasks.collect_all_servers",
            "schedule": settings.default_monitoring_interval,
        },
        "cleanup-old-metrics": {
            "task": "app.workers.tasks.cleanup_old_metrics",
            "schedule": 86400,
        },
    },
)

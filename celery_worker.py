from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["tasks.celery_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


celery_app.conf.beat_schedule = {
    "delete-expired-tasks-every-hour": {
        "task": "tasks.schedules.delete_expired_tasks",
        "schedule": crontab(minute=0, hour="*"),  # щогодини
    },
}
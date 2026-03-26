from datetime import datetime, timezone, timedelta

from sqlalchemy import select

from celery_worker import celery_app
from database import SyncSessionLocal
from tasks.models import Task
from tasks.celery_tasks import send_deadline_missed_email


@celery_app.task
def delete_expired_tasks():
    db = SyncSessionLocal()
    try:
        now = datetime.now(timezone.utc)
        stmt = select(Task).where(
            Task.due_date < now,
            Task.is_completed == False,
        )
        expired = db.execute(stmt).scalars().all()

        for task in expired:
            if task.email:
                send_deadline_missed_email.delay(
                    task.email, task.title, task.due_date
                )
            db.delete(task)

        db.commit()
        return f"Deleted {len(expired)} expired tasks"
    finally:
        db.close()


@celery_app.task
def process_recurring_tasks():
    db = SyncSessionLocal()
    try:
        now = datetime.now(timezone.utc)

        stmt = select(Task).where(
            Task.is_recurring.is_(True),
            Task.next_run_at.is_not(None),
            Task.next_run_at <= now,
        )
        tasks = db.execute(stmt).scalars().all()

        for task in tasks:
            # зсуваємо наступний запуск у поточної задачі
            task.next_run_at = task.next_run_at + timedelta(
                days=task.repeat_every_days or 1
            )

        db.commit()
        return f"Processed {len(tasks)} recurring tasks"
    finally:
        db.close()

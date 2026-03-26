from datetime import datetime, timezone, timedelta

from sqlalchemy import select

from celery_worker import celery_app
from database import SyncSessionLocal
from tasks.models import Task
from tasks.celery_tasks import send_deadline_missed_email, send_deadline_reminder_email

DEADLINE_REMINDER_MINUTES = 15


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


@celery_app.task
def send_deadline_reminders():
    db = SyncSessionLocal()
    try:
        now = datetime.now(timezone.utc)
        reminder_from = now + timedelta(minutes=DEADLINE_REMINDER_MINUTES)

        stmt = select(Task).where(
            Task.is_completed == False,
            Task.email.is_not(None),
            Task.due_date.is_not(None),
            Task.deadline_reminder_sent_at.is_(None),
            Task.due_date >= now,
            Task.due_date <= reminder_from,
        )
        tasks = db.execute(stmt).scalars().all()

        for task in tasks:
            send_deadline_reminder_email.delay(
                task.email,
                task.title,
                task.due_date,
            )
            task.deadline_reminder_sent_at = now

        db.commit()
        return f"Sent {len(tasks)} deadline reminders"
    finally:
        db.close()

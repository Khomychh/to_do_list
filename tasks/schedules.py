from datetime import datetime, timezone

from sqlalchemy import select

from celery_worker import celery_app
from database import SessionLocal
from tasks.models import Task
from tasks.celery_tasks import send_deadline_missed_email


@celery_app.task
def delete_expired_tasks():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        stmt = select(Task).where(Task.due_date < now, Task.is_completed == False)
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

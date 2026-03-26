import asyncio
from datetime import datetime

from fastapi_mail import FastMail, MessageSchema, MessageType

from celery_worker import celery_app
from config import mail_config


@celery_app.task
def send_task_completed_email(email: str, task_title: str):
    message = MessageSchema(
        subject="Завдання виконано",
        recipients=[email],
        body=f"Завдання «{task_title}» було позначено як виконане.",
        subtype=MessageType.plain,
    )
    fm = FastMail(mail_config)

    asyncio.run(fm.send_message(message))


@celery_app.task
def send_deadline_missed_email(email: str, task_title: str, deadline: datetime):
    message = MessageSchema(
        subject="Дедлайн пропущено",
        recipients=[email],
        body=f"Дедлайн для завдання «{task_title}» ({deadline.strftime('%d.%m.%Y %H:%M')}) вже минув!",
        subtype=MessageType.plain,
    )
    fm = FastMail(mail_config)

    asyncio.run(fm.send_message(message))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.models import Task
from tasks.schemas import TaskCreate, TaskUpdate, TaskRead


async def get_all_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
):
    stmt = select(Task).offset(skip).limit(limit)

    if status == "completed":
        stmt = stmt.where(Task.is_completed == True)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_task(db: AsyncSession, task_id: int) -> TaskRead | None:
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_task(db: AsyncSession, task_in: TaskCreate):
    db_task = Task(**task_in.model_dump())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_task(db: AsyncSession, task_id: int, task_in: TaskUpdate):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if task is None:
        return None

    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def complete_task(db: AsyncSession, task_id: int) -> TaskRead | None:
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        return None

    task.is_completed = True
    await db.commit()
    await db.refresh(task)
    return task


async def uncomplete_task(db: AsyncSession, task_id: int) -> TaskRead | None:
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if task is None:
        return None

    task.is_completed = False
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if task is None:
        return False

    await db.delete(task)
    await db.commit()
    return True

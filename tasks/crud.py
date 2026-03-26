from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.models import Task, Tag
from tasks.schemas import TaskCreate, TaskUpdate, TaskRead, TagCreate


async def _get_tags_by_ids(db: AsyncSession, tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []

    stmt = select(Tag).where(Tag.id.in_(tag_ids))
    result = await db.execute(stmt)
    tags = list(result.scalars().all())

    if len(tags) != len(set(tag_ids)):
        found_ids = {tag.id for tag in tags}
        missing_ids = [tag_id for tag_id in tag_ids if tag_id not in found_ids]
        raise ValueError(f"Теги не знайдено: {missing_ids}")

    return tags


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


async def get_task(db: AsyncSession, task_id: int):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_task(db: AsyncSession, task_in: TaskCreate):
    task_data = task_in.model_dump(exclude={"tag_ids"})
    db_task = Task(**task_data)

    db_task.tags = await _get_tags_by_ids(db, task_in.tag_ids)

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

    if task_in.tag_ids is not None:
        task.tags = await _get_tags_by_ids(db, task_in.tag_ids)

    await db.commit()
    await db.refresh(task)
    return task


async def complete_task(db: AsyncSession, task_id: int):
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        return None

    task.is_completed = True
    await db.commit()
    await db.refresh(task)
    return task


async def uncomplete_task(db: AsyncSession, task_id: int):
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


async def get_all_tags(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Tag).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_tag(db: AsyncSession, tag_in: TagCreate):
    db_tag = Tag(**tag_in.model_dump())
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag


async def delete_tag(db: AsyncSession, tag_id: int) -> bool:
    stmt = select(Tag).where(Tag.id == tag_id)
    result = await db.execute(stmt)
    tag = result.scalar_one_or_none()
    if tag is None:
        return False

    await db.delete(tag)
    await db.commit()
    return True

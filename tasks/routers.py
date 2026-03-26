from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db, Pagination, pagination_params
from tasks import crud
from tasks.schemas import TaskRead, TaskCreate, TaskUpdate, TagRead, TagCreate
from tasks.celery_tasks import send_task_completed_email

router = APIRouter()


@router.get("/tasks", response_model=list[TaskRead], status_code=200)
async def list_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[Pagination, Depends(pagination_params)],
    status: str | None = Query(None, description="Filter by status"),
):
    return await crud.get_all_tasks(
        db, pagination.skip, pagination.limit, status=status
    )


@router.get("/tasks/{task_id}", response_model=TaskRead, status_code=200)
async def read_task(db: Annotated[AsyncSession, Depends(get_db)], task_id: int):
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/tasks", response_model=TaskRead, status_code=201)
async def create_task(
    db: Annotated[AsyncSession, Depends(get_db)],
    task: TaskCreate,
):
    return await crud.create_task(db, task)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)
):
    task = await crud.update_task(db, task_id, task)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
async def complete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await crud.complete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.email:
        send_task_completed_email.delay(task.email, task.title)

    return task


@router.patch("/tasks/{task_id}/uncomplete", response_model=TaskRead)
async def uncomplete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await crud.uncomplete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    db: Annotated[AsyncSession, Depends(get_db)],
    task_id: int,
):
    success = await crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


@router.get("/tags", response_model=list[TagRead], status_code=200)
async def list_tags(
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[Pagination, Depends(pagination_params)],
) -> list[TagRead]:
    tags = await crud.get_all_tags(db, pagination.skip, pagination.limit)
    return tags


@router.post("/tags", response_model=TagRead, status_code=201)
async def create_tag(
    db: Annotated[AsyncSession, Depends(get_db)],
    tag_in: TagCreate,
) -> TagRead:
    tag = await crud.create_tag(db, tag_in)
    return tag


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(
    db: Annotated[AsyncSession, Depends(get_db)],
    tag_id: int,
) -> None:
    success = await crud.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return

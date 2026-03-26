from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

from tasks.models import TaskPriority


class TagBase(BaseModel):
    name: str = Field(min_length=1)


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    email: Optional[EmailStr] = None
    priority: TaskPriority = TaskPriority.medium
    tag_ids: list[int] = Field(default_factory=list)

    is_recurring: bool = False
    repeat_every_days: Optional[int] = None
    next_run_at: Optional[datetime] = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    due_date: Optional[datetime]
    email: Optional[EmailStr] = None
    created_at: datetime
    priority: TaskPriority
    tags: list[TagRead] = Field(default_factory=list)

    is_recurring: bool
    repeat_every_days: Optional[int] = None
    next_run_at: Optional[datetime] = None

    deadline_reminder_sent_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    email: Optional[EmailStr] = None
    priority: Optional[TaskPriority] = None
    tag_ids: Optional[list[int]] = None

    is_recurring: Optional[bool] = None
    repeat_every_days: Optional[int] = None
    next_run_at: Optional[datetime] = None
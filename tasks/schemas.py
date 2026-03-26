from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

from tasks.models import TaskPriority


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    email: Optional[EmailStr] = None
    priority: TaskPriority = TaskPriority.medium


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    due_date: Optional[datetime]
    email: Optional[EmailStr] = None
    created_at: datetime
    priority: TaskPriority

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    email: Optional[EmailStr] = None
    priority: Optional[TaskPriority] = None

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool
    due_date: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None

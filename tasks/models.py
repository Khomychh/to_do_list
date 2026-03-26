from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class Task(Base):
    __tablename__ = "tasks"


    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )

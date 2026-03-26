from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./todo.db"
SYNC_DATABASE_URL = "sqlite:///./todo.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# Для Celery
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass

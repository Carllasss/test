from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import asyncio

from app.config.settings import settings

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.SQL_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_async_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    """Асинхронный генератор сессий"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инит базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        print("Database connection established")
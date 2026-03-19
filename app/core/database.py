import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text
from typing import AsyncGenerator

from app.core.config import settings
from app.core.logger import get_custom_logger

logger = get_custom_logger(app_name="database")

if settings.MSSQL_URL:
    DATABASE_URL = settings.MSSQL_URL
    logger.info("Using MSSQL database")
else:
    DATABASE_URL = "sqlite+aiosqlite://"
    logger.warning("No MSSQL_URL configured — using in-memory SQLite (DB features disabled)")


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def init_db() -> None:
    if not settings.MSSQL_URL:
        logger.warning("Database skipped — no MSSQL_URL configured")
        return

    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

    logger.info("Database connection verified")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

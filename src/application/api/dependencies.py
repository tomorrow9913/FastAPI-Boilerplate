# -*- coding: utf-8 -*-
# src/application/api/dependencies.py
# get_session, get_redis, DI
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import config
from src.infrastructure.database.models import Base

engine = {
    "WRITER": create_async_engine(config.DATABASE_CONFIG.WRITER_DB_URL),
}


async_session_maker = async_sessionmaker(
    bind=engine.get("WRITER"), expire_on_commit=False
)


async def create_db_and_tables():
    async with engine["WRITER"].begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

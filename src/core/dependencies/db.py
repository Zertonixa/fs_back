from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import async_session_maker
from src.core.db.uow import UoW


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_uow() -> AsyncGenerator[UoW, None]:
    async with async_session_maker() as session:
        yield UoW(session)

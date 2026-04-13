from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import async_session_maker
from src.core.db.uow import UoW
from src.core.events.bus import EventBus


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


async def get_uow(
    session: AsyncSession = Depends(get_async_session), event_bus: EventBus = Depends(get_event_bus)
) -> AsyncGenerator[UoW, None]:
    yield UoW(session=session, event_bus=event_bus)

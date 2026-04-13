from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.events.bus import EventBus


class UoW:
    def __init__(self, session: AsyncSession, event_bus: EventBus):
        self.session = session
        self._event_bus = event_bus
        self._events: list[Any] = []

    def add_event(self, event: Any) -> None:
        self._events.append(event)

    async def _dispatch_events(self) -> None:
        events = self._events
        self._events = []
        for e in events:
            await self._event_bus.publish(e)

    @asynccontextmanager
    async def transaction(self):
        try:
            yield self
            await self.session.commit()
        except Exception:
            self._events = []
            await self.session.rollback()
            raise
        else:
            await self._dispatch_events()

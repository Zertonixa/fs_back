from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.adapters.s3.service import S3Service
from src.apps.admin.events import AdminActionEvent

# from src.core.events.types import SlotUpdatedEvent
# from src.apps.booking.repositories.sql.booking import BookingRepo
from src.apps.admin_history.handlers import AdminHistoryHandler
from src.apps.admin_history.repositories.sql.admin_history import AdminHistoryRepo
from src.core.dependencies import get_async_session
from src.core.events.bus import EventBus


@asynccontextmanager
async def lifespan(app: FastAPI):
    bus = EventBus()
    app.state.event_bus = bus

    async def handle_admin_action(event: AdminActionEvent) -> None:
        async for session in get_async_session():
            repo = AdminHistoryRepo(session)
            handler = AdminHistoryHandler(repo)
            await handler.on_admin_action(event)
            await session.commit()

    bus.subscribe(AdminActionEvent, handle_admin_action)

    s3_service = S3Service()
    await s3_service.ensure_bucket_exists()

    # async def handle_slot_updated(event: SlotUpdatedEvent) -> None:
    #     async for session in get_async_session():
    #         repo = BookingRepo(session)
    #         handler = CancelBookingsOnSlotUpdated(repo)
    #         await handler.handle(event)
    #         await session.commit()

    # bus.subscribe(SlotUpdatedEvent, handle_slot_updated)

    yield

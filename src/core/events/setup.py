from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.admin_history.handlers import AdminHistoryHandler
from src.apps.admin_history.repositories.sql.admin_history import AdminHistoryRepo
from src.core.events.bus import EventBus
from src.core.events.types import AdminActionEvent


def build_event_bus(session: AsyncSession) -> EventBus:
    bus = EventBus()
    history_repo = AdminHistoryRepo(session)
    handler = AdminHistoryHandler(history_repo)
    bus.subscribe(AdminActionEvent, handler.on_admin_action)
    return bus

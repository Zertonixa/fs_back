from src.core.events.bus import EventBus

from .handlers import AdminActionEvent, AdminHistoryHandler
from .repositories.interfaces import IAdminHistoryRepo


def register_admin_history(bus: EventBus, history_repo: IAdminHistoryRepo):
    handler = AdminHistoryHandler(history_repo)
    bus.subscribe(AdminActionEvent, handler.handle)

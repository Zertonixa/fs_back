from src.apps.admin.events import AdminActionEvent
from src.apps.admin_history.repositories.interfaces import IAdminHistoryRepo


class AdminHistoryHandler:
    def __init__(self, repo: IAdminHistoryRepo):
        self.repo = repo

    async def on_admin_action(self, event: AdminActionEvent) -> None:
        await self.repo.add(
            moderator_id=event.moderator_id,
            action=event.action,
            description=event.description,
            target_user_id=event.target_user_id,
            slot_id=event.slot_id,
        )

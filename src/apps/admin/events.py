from dataclasses import dataclass
from uuid import UUID

from src.core.db.models.admin_history import AdminAction


@dataclass(slots=True)
class AdminActionEvent:
    moderator_id: UUID
    action: AdminAction
    description: str
    target_user_id: UUID | None = None
    slot_id: UUID | None = None

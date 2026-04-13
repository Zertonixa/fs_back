from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class AdminAction(StrEnum):
    BAN = "ban"
    UNBAN = "unban"
    GRANT_ADMIN = "grant_admin"
    REVOKE_ADMIN = "revoke_admin"
    CHANGE_SLOT = "change_slot"


@dataclass(frozen=True)
class AdminActionEvent:
    moderator_id: UUID
    action: AdminAction
    description: str
    slot_id: UUID | None = None
    target_user_id: UUID | None = None


@dataclass(frozen=True)
class SlotUpdatedEvent:
    slot_id: UUID
    moderator_id: UUID

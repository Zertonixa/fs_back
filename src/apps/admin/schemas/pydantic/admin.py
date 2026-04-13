from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.db.models.admin_history import AdminAction


class AdminUser(BaseModel):
    id: UUID
    telegram_id: int
    username: str | None
    is_banned: bool
    created_at: datetime
    updated_at: datetime
    is_admin: bool


class AdminUserUpdate(BaseModel):
    username: str | None = None
    is_banned: bool | None = None


class AdminHistoryOut(BaseModel):
    id: UUID
    moderator_id: UUID
    created_at: datetime
    action: AdminAction
    description: str
    slot_id: UUID | None = None
    target_user_id: UUID | None = None

    class Config:
        from_attributes = True

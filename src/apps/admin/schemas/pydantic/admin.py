from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdminUser(BaseModel):
    id: UUID
    telegram_id: int
    username: str | None
    is_banned: bool
    created_at: datetime
    updated_at: datetime


class AdminUserUpdate(BaseModel):
    username: str | None = None
    is_banned: bool | None = None

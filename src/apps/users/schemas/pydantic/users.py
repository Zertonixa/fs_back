from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    telegram_id: int
    username: str | None
    created_at: datetime
    updated_at: datetime
    is_banned: bool
    is_admin: bool

    class Config:
        from_attributes = True

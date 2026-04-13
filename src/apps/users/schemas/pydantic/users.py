from datetime import datetime
from math import ceil
from typing import Self
from uuid import UUID

from pydantic import BaseModel, computed_field


class User(BaseModel):
    id: UUID
    telegram_id: int
    username: str | None = None
    is_banned: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BanInfo(BaseModel):
    is_banned: bool
    banned_at: datetime | None = None
    description: str | None = None
    moderator_id: UUID | None = None
    moderator_username: str | None = None


class PaginatedUsersResponse(BaseModel):
    items: list[User]
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool

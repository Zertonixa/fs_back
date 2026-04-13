from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BanInfo(BaseModel):
    is_banned: bool
    banned_at: datetime | None = None
    description: str | None = None
    moderator_id: UUID | None = None
    moderator_username: str | None = None

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    telegram_id: int
    username: str
    created_at: datetime
    ends_at: datetime


class UserDelete(BaseModel):
    id: UUID

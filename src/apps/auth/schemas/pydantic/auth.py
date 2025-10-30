from uuid import UUID

from pydantic import BaseModel


class TelegramAuthIn(BaseModel):
    user_id: UUID
    user_name: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    telegram_id: int
    username: str

from pydantic import BaseModel, Field


class TelegramAuthIn(BaseModel):
    init_data: str = Field(alias="initData")


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    telegram_id: int
    username: str
    is_admin: bool
    is_root_admin: bool

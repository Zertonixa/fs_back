from pydantic import BaseModel, ConfigDict, Field


class TelegramAuthIn(BaseModel):
    init_data: str = Field(alias="initData")

    model_config = ConfigDict(populate_by_name=True)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    telegram_id: int
    username: str

from abc import ABC, abstractmethod
from typing import Optional

from src.core.db.models import Users

from ..schemas.dataclasses import TgUserPayload


class IUserRepo(ABC):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional["Users"]: ...

    @abstractmethod
    async def upsert_by_telegram(self, payload: TgUserPayload) -> "Users": ...

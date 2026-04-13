from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.core.db.models import AuthSession, Users

from ..schemas.dataclasses.auth import TgUserPayload


class IUserRepo(ABC):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Users | None: ...

    @abstractmethod
    async def upsert_by_telegram(self, payload: TgUserPayload) -> Users: ...


class IAuthSessionRepo(ABC):
    @abstractmethod
    async def create(
        self,
        user_id: UUID,
        jti: UUID,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> AuthSession: ...

    @abstractmethod
    async def get_by_jti(self, jti: UUID) -> AuthSession | None: ...

    @abstractmethod
    async def revoke(self, jti: UUID) -> None: ...

    @abstractmethod
    async def revoke_all_by_user(self, user_id: UUID) -> None: ...

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from src.core.db.models import Users


class IAdminUserRepo(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Users | None: ...

    @abstractmethod
    async def set_ban(self, user_id: UUID, banned: bool) -> Users: ...

    @abstractmethod
    async def update_user(
        self,
        user_id: UUID,
        *,
        username: str | None = None,
        is_banned: bool | None = None,
    ) -> Users: ...

    @abstractmethod
    async def list_users(self) -> Sequence[Users]: ...

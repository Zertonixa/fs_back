from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Literal
from uuid import UUID

from src.core.db.models import Users


class IUserRepo(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Users | None: ...

    @abstractmethod
    async def list_users(
        self,
        *,
        name: str | None = None,
        is_banned: bool | None = None,
        is_admin: bool | None = None,
        sort_by: Literal["created_at", "updated_at"] = "created_at",
        sort_order: Literal["asc", "desc"] = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[Sequence[Users], int]: ...

    @abstractmethod
    async def create_user(self, user: Users) -> Users: ...

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None: ...
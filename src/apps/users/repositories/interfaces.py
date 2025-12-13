from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from src.core.db.models import Users


class IUserRepo(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Users | None: ...

    @abstractmethod
    async def list_users(self) -> Sequence[Users]: ...

    @abstractmethod
    async def create_user(self, user: Users) -> Users: ...

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None: ...

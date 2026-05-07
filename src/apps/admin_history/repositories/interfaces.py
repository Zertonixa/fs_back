from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from src.core.db.models.admin_history import AdminAction, AdminHistory


class IAdminHistoryRepo(ABC):
    @abstractmethod
    async def add(
        self,
        *,
        moderator_id: UUID,
        action: AdminAction,
        description: str,
        slot_id: UUID | None = None,
        target_user_id: UUID | None = None,
    ) -> AdminHistory: ...

    @abstractmethod
    async def list(
        self,
        *,
        limit: int,
        offset: int,
        moderator_id: UUID | None = None,
        target_user_id: UUID | None = None,
        action: AdminAction | None = None,
    ) -> Sequence[AdminHistory]: ...

    @abstractmethod
    async def get_last_ban_for_user(self, user_id: UUID) -> AdminHistory | None: ...

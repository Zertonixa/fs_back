from uuid import UUID

from fastapi import HTTPException, status

from src.core.db.models import Users
from src.core.db.uow import UoW

from ..repositories.interfaces import IAdminUserRepo


class AdminService:
    def __init__(self, repo: IAdminUserRepo, uow: UoW):
        self.repo = repo
        self.uow = uow

    async def _get_or_404(self, user_id: UUID) -> Users:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def ban_user(self, user_id: UUID) -> Users:
        async with self.uow.transaction():
            await self._get_or_404(user_id)
            user = await self.repo.set_ban(user_id, True)
            return user

    async def unban_user(self, user_id: UUID) -> Users:
        async with self.uow.transaction():
            await self._get_or_404(user_id)
            user = await self.repo.set_ban(user_id, False)
            return user

    async def edit_user(
        self, user_id: UUID, *, username: str | None = None, is_banned: bool | None = None
    ) -> Users:
        async with self.uow.transaction():
            await self._get_or_404(user_id)
            user = await self.repo.update_user(user_id, username=username, is_banned=is_banned)
            return user

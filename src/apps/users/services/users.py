from collections.abc import Sequence
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db.models import Users
from src.core.db.uow import UoW

from ..repositories.interfaces import IUserRepo


class UserService:
    def __init__(self, repo: IUserRepo, uow: UoW) -> None:
        self.repo = repo
        self.uow = uow

    async def _get_or_404(self, user_id: UUID) -> Users:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def get_all_users(self) -> list[Users]:
        async with self.uow.transaction():
            users: Sequence[Users] = await self.repo.list_users()
            return list(users)

    async def create_user(self, data: dict[str, Any]) -> Users:
        async with self.uow.transaction():
            user = Users(**data)
            return await self.repo.create_user(user)

    async def delete_user(self, user_id: int) -> None:
        async with self.uow.transaction():
            await self._get_or_404(user_id)
            await self.repo.delete_user(user_id)

from math import ceil
from typing import Any, Literal
from uuid import UUID

from fastapi import HTTPException, status

from src.apps.admin_history.repositories.interfaces import IAdminHistoryRepo
from src.apps.users.schemas.pydantic.users import BanInfo, PaginatedUsersResponse, User
from src.core.db.models import Users
from src.core.db.uow import UoW

from ..repositories.interfaces import IUserRepo


class UserService:
    def __init__(self, repo: IUserRepo, admin_history_repo: IAdminHistoryRepo, uow: UoW) -> None:
        self.repo = repo
        self.admin_history_repo = admin_history_repo
        self.uow = uow

    async def _get_or_404(self, user_id: UUID) -> Users:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def get_all_users(
        self,
        *,
        name: str | None = None,
        is_banned: bool | None = None,
        is_admin: bool | None = None,
        sort_by: Literal["created_at", "updated_at"] = "created_at",
        sort_order: Literal["asc", "desc"] = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedUsersResponse:
        async with self.uow.transaction():
            users, total = await self.repo.list_users(
                name=name,
                is_banned=is_banned,
                is_admin=is_admin,
                sort_by=sort_by,
                sort_order=sort_order,
                page=page,
                per_page=per_page,
            )

            pages = ceil(total / per_page) if total > 0 else 1

            return PaginatedUsersResponse(
                items=[User.model_validate(user) for user in users],
                page=page,
                per_page=per_page,
                total=total,
                pages=pages,
                has_next=page < pages,
            )

    async def create_user(self, data: dict[str, Any]) -> Users:
        async with self.uow.transaction():
            user = Users(**data)
            return await self.repo.create_user(user)

    async def delete_user(self, user_id: UUID) -> None:
        async with self.uow.transaction():
            await self._get_or_404(user_id)
            await self.repo.delete_user(user_id)

    async def get_my_ban_info(self, user_id: UUID) -> BanInfo:
        async with self.uow.transaction():
            user = await self._get_or_404(user_id)

            if not user.is_banned:
                return BanInfo(is_banned=False)

            last_ban = await self.admin_history_repo.get_last_ban_for_user(user.id)

            if last_ban is None:
                return BanInfo(is_banned=True)

            return BanInfo(
                is_banned=True,
                banned_at=last_ban.created_at,
                description=last_ban.description,
                moderator_id=last_ban.moderator_id,
                moderator_username=getattr(last_ban.moderator, "username", None),
            )

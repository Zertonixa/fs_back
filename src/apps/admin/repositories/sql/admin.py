from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.admin.repositories.interfaces import IAdminUserRepo
from src.core.db.models import Users


class AdminUserRepo(IAdminUserRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Users | None:
        return await Users.get_by_id(self.session, user_id)

    async def set_ban(self, user_id: UUID, banned: bool) -> Users:
        user = await self.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        user.is_banned = banned
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_user(
        self, user_id: UUID, *, username: str | None = None, is_banned: bool | None = None
    ) -> Users:
        user = await self.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        if username is not None:
            user.username = username
        if is_banned is not None:
            user.is_banned = is_banned

        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def set_admin_role(self, user_id: UUID, make_admin: bool) -> Users:
        user = await self.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        user.is_admin = make_admin
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list_users(self) -> Sequence[Users]:
        result = await self.session.execute(select(Users))
        return list(result.scalars().all())

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Users

from ..interfaces import IAdminUserRepo


class AdminUserRepo(IAdminUserRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Users | None:
        user = await Users.get_by_id(self.session, user_id)
        return user

    async def set_ban(self, user_id: UUID, banned: bool) -> Users:
        user = await self.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        user.is_banned = banned
        await self.session.flush()
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
        return user

    async def list_users(self) -> Sequence[Users]:
        stmt = select(Users)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

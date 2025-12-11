from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Users

from ..interfaces import IUserRepo


class UserRepo(IUserRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Users | None:
        stmt = Users.get_by_id(user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(self) -> Sequence[Users]:
        stmt = select(Users)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_user(self, user: Users) -> Users:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        if user is None:
            raise ValueError("user not found")

        await self.session.delete(user)
        await self.session.flush()

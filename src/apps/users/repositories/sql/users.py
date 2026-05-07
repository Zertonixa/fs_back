from collections.abc import Sequence
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Users

from ..interfaces import IUserRepo


class UserRepo(IUserRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Users | None:
        return await Users.get_by_id(self.session, user_id)

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
    ) -> tuple[Sequence[Users], int]:
        stmt = select(Users)
        count_stmt = select(func.count()).select_from(Users)

        filters = []

        if name:
            filters.append(Users.username.ilike(f"%{name}%"))

        if is_banned is not None:
            filters.append(Users.is_banned == is_banned)

        if is_admin is not None:
            filters.append(Users.is_admin == is_admin)

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        sort_column = getattr(Users, sort_by)
        stmt = stmt.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())

        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        result = await self.session.execute(stmt)
        users = list(result.scalars().all())

        return users, total

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

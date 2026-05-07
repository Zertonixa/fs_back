from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.auth.repositories.interfaces import IUserRepo
from src.apps.auth.schemas.dataclasses.auth import TgUserPayload
from src.core.db.models import Users


class UserRepo(IUserRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Users | None:
        stmt = select(Users).where(Users.telegram_id == telegram_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def upsert_by_telegram(self, payload: TgUserPayload) -> Users:
        user = await self.get_by_telegram_id(payload.telegram_id)
        now = datetime.now(UTC)

        if user is None:
            user = Users(
                telegram_id=payload.telegram_id,
                username=payload.username,
                created_at=now,
                updated_at=now,
                is_admin=False,
                is_banned=False,
            )
            self.session.add(user)
        else:
            user.username = payload.username
            user.updated_at = now

        await self.session.flush()
        return user

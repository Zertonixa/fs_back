from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.apps.admin_history.repositories.interfaces import IAdminHistoryRepo
from src.core.db.models.admin_history import AdminAction, AdminHistory


class AdminHistoryRepo(IAdminHistoryRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_last_ban_for_user(self, user_id: UUID) -> AdminHistory | None:
        stmt = (
            select(AdminHistory)
            .where(AdminHistory.target_user_id == user_id, AdminHistory.action == AdminAction.BAN)
            .order_by(desc(AdminHistory.created_at))
            .limit(1)
            .options(selectinload(AdminHistory.moderator))
        )

        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

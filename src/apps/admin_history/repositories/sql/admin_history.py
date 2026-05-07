from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.apps.admin_history.repositories.interfaces import IAdminHistoryRepo
from src.core.db.models.admin_history import AdminAction, AdminHistory


class AdminHistoryRepo(IAdminHistoryRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
        self,
        *,
        moderator_id: UUID,
        action: AdminAction,
        description: str,
        slot_id: UUID | None = None,
        target_user_id: UUID | None = None,
    ) -> AdminHistory:
        row = AdminHistory(
            moderator_id=moderator_id,
            action=action,
            description=description,
            slot_id=slot_id,
            target_user_id=target_user_id,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return row

    async def list(
        self,
        *,
        limit: int,
        offset: int,
        moderator_id: UUID | None = None,
        target_user_id: UUID | None = None,
        action: AdminAction | None = None,
    ) -> Sequence[AdminHistory]:
        stmt = select(AdminHistory).order_by(desc(AdminHistory.created_at))

        if moderator_id is not None:
            stmt = stmt.where(AdminHistory.moderator_id == moderator_id)
        if target_user_id is not None:
            stmt = stmt.where(AdminHistory.target_user_id == target_user_id)
        if action is not None:
            stmt = stmt.where(AdminHistory.action == action)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

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

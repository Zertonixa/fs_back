from uuid import UUID

from fastapi import HTTPException, status

from src.apps.admin.events import AdminActionEvent
from src.apps.admin.repositories.interfaces import IAdminUserRepo
from src.apps.admin_history.repositories.interfaces import IAdminHistoryRepo
from src.core.db.models import Users
from src.core.db.models.admin_history import AdminAction
from src.core.db.uow import UoW
from src.core.dependencies.admin import is_root_admin_tg


class AdminService:
    def __init__(self, repo: IAdminUserRepo, history_repo: IAdminHistoryRepo, uow: UoW):
        self.repo = repo
        self.history_repo = history_repo
        self.uow = uow

    async def _get_or_404(self, user_id: UUID) -> Users:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def _assert_root(self, current_admin_tg: int | None):
        if not is_root_admin_tg(current_admin_tg):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Only root admin allowed"
            )

    async def ban_user(
        self, user_id: UUID, *, current_admin_id: UUID, current_admin_tg: int | None
    ) -> Users:
        async with self.uow.transaction():
            if user_id == current_admin_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot ban yourself"
                )

            target = await self._get_or_404(user_id)

            if is_root_admin_tg(target.telegram_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Root admin cannot be banned"
                )

            if target.is_admin and not is_root_admin_tg(current_admin_tg):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Only root admin can ban admins"
                )

            user = await self.repo.set_ban(user_id, True)

            self.uow.add_event(
                AdminActionEvent(
                    moderator_id=current_admin_id,
                    action=AdminAction.BAN,
                    description=f"Banned user {user_id}",
                    target_user_id=user_id,
                )
            )

            return user

    async def unban_user(
        self, user_id: UUID, *, current_admin_id: UUID, current_admin_tg: int | None
    ) -> Users:
        async with self.uow.transaction():
            target = await self._get_or_404(user_id)

            if is_root_admin_tg(target.telegram_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Root admin cannot be modified"
                )

            if target.is_admin and not is_root_admin_tg(current_admin_tg):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Only root admin can unban admins"
                )

            user = await self.repo.set_ban(user_id, False)

            self.uow.add_event(
                AdminActionEvent(
                    moderator_id=current_admin_id,
                    action=AdminAction.UNBAN,
                    description=f"Unbanned user {user_id}",
                    target_user_id=user_id,
                )
            )

            return user

    async def edit_user(
        self,
        user_id: UUID,
        *,
        username: str | None = None,
        is_banned: bool | None = None,
        current_admin_id: UUID,
        current_admin_tg: int | None,
    ) -> Users:
        async with self.uow.transaction():
            target = await self._get_or_404(user_id)

            if is_root_admin_tg(target.telegram_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Root admin cannot be edited"
                )

            if target.is_admin and not is_root_admin_tg(current_admin_tg):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Only root admin can edit admins"
                )

            user = await self.repo.update_user(user_id, username=username, is_banned=is_banned)

            if is_banned is True:
                action = AdminAction.BAN
                desc = f"Edited user {user_id}: set banned=True"
            elif is_banned is False:
                action = AdminAction.UNBAN
                desc = f"Edited user {user_id}: set banned=False"
            else:
                action = AdminAction.CHANGE_SLOT
                desc = f"Edited user {user_id}"

            self.uow.add_event(
                AdminActionEvent(
                    moderator_id=current_admin_id,
                    action=action,
                    description=desc,
                    target_user_id=user_id,
                )
            )

            return user

    async def toggle_admin_role(
        self, user_id: UUID, *, current_admin_id: UUID, current_admin_tg: int | None
    ) -> Users:
        self._assert_root(current_admin_tg)

        async with self.uow.transaction():
            target = await self._get_or_404(user_id)

            if is_root_admin_tg(target.telegram_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Root admin role cannot be changed",
                )

            make_admin = not target.is_admin
            user = await self.repo.set_admin_role(user_id, make_admin=make_admin)

            self.uow.add_event(
                AdminActionEvent(
                    moderator_id=current_admin_id,
                    action=AdminAction.GRANT_ADMIN if make_admin else AdminAction.REVOKE_ADMIN,
                    description=("Granted admin role" if make_admin else "Revoked admin role")
                    + f" for user {user_id}",
                    target_user_id=user_id,
                )
            )

            return user

    async def get_history(
        self,
        *,
        limit: int,
        offset: int,
        moderator_id: UUID | None = None,
        target_user_id: UUID | None = None,
        action: AdminAction | None = None,
    ):
        return await self.history_repo.list(
            limit=limit,
            offset=offset,
            moderator_id=moderator_id,
            target_user_id=target_user_id,
            action=action,
        )

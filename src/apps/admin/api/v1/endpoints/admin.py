from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.apps.admin.di import get_admin_service
from src.apps.admin.schemas.pydantic.admin import AdminUser, AdminUserUpdate
from src.apps.admin.services import AdminService
from src.core.db.models import Users
from src.core.dependencies.admin import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


def _to_admin_user(user: Users) -> AdminUser:
    return AdminUser(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        is_banned=user.is_banned,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.patch("/ban/{user_id}", status_code=status.HTTP_200_OK, response_model=AdminUser)
async def ban_user(
    user_id: UUID, admin_service: AdminService = Depends(get_admin_service)
) -> AdminUser:
    user = await admin_service.ban_user(user_id)
    return _to_admin_user(user)


@router.patch("/unban/{user_id}", status_code=status.HTTP_200_OK, response_model=AdminUser)
async def unban_user(
    user_id: UUID, admin_service: AdminService = Depends(get_admin_service)
) -> AdminUser:
    user = await admin_service.unban_user(user_id)
    return _to_admin_user(user)


@router.patch("/edit/{user_id}", status_code=status.HTTP_200_OK, response_model=AdminUser)
async def edit_user(
    user_id: UUID, data: AdminUserUpdate, admin_service: AdminService = Depends(get_admin_service)
) -> AdminUser:
    user = await admin_service.edit_user(user_id, username=data.username, is_banned=data.is_banned)
    return _to_admin_user(user)

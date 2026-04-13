from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.apps.admin.di import get_admin_service
from src.apps.admin.schemas.pydantic.admin import AdminHistoryOut, AdminUser, AdminUserUpdate
from src.apps.admin.services.admin import AdminService
from src.core.db.models import Users
from src.core.db.models.admin_history import AdminAction
from src.core.dependencies.admin import require_admin
from src.core.dependencies.user import get_current_telegram_id, get_current_user_id

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


def _to_admin_user(user: Users) -> AdminUser:
    return AdminUser(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        is_banned=user.is_banned,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.patch("/ban/{user_id}", response_model=AdminUser)
async def ban_user(
    user_id: UUID,
    admin_service: AdminService = Depends(get_admin_service),
    current_admin_id: UUID = Depends(get_current_user_id),
    current_admin_tg: int | None = Depends(get_current_telegram_id),
) -> AdminUser:
    user = await admin_service.ban_user(
        user_id, current_admin_id=current_admin_id, current_admin_tg=current_admin_tg
    )
    return _to_admin_user(user)


@router.patch("/unban/{user_id}", response_model=AdminUser)
async def unban_user(
    user_id: UUID,
    admin_service: AdminService = Depends(get_admin_service),
    current_admin_id: UUID = Depends(get_current_user_id),
    current_admin_tg: int | None = Depends(get_current_telegram_id),
) -> AdminUser:
    user = await admin_service.unban_user(
        user_id, current_admin_id=current_admin_id, current_admin_tg=current_admin_tg
    )
    return _to_admin_user(user)


@router.patch("/edit/{user_id}", response_model=AdminUser)
async def edit_user(
    user_id: UUID,
    data: AdminUserUpdate,
    admin_service: AdminService = Depends(get_admin_service),
    current_admin_id: UUID = Depends(get_current_user_id),
    current_admin_tg: int | None = Depends(get_current_telegram_id),
) -> AdminUser:
    user = await admin_service.edit_user(
        user_id,
        username=data.username,
        is_banned=data.is_banned,
        current_admin_id=current_admin_id,
        current_admin_tg=current_admin_tg,
    )
    return _to_admin_user(user)


@router.patch("/role/{user_id}/toggle", response_model=AdminUser)
async def toggle_admin_role(
    user_id: UUID,
    admin_service: AdminService = Depends(get_admin_service),
    current_admin_id: UUID = Depends(get_current_user_id),
    current_admin_tg: int | None = Depends(get_current_telegram_id),
) -> AdminUser:
    user = await admin_service.toggle_admin_role(
        user_id, current_admin_id=current_admin_id, current_admin_tg=current_admin_tg
    )
    return _to_admin_user(user)


@router.get("/history", response_model=list[AdminHistoryOut])
async def get_admin_history(
    admin_service: AdminService = Depends(get_admin_service),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    moderator_id: UUID | None = Query(None),
    target_user_id: UUID | None = Query(None),
    action: AdminAction | None = Query(None),
) -> list[AdminHistoryOut]:
    items = await admin_service.get_history(
        limit=limit,
        offset=offset,
        moderator_id=moderator_id,
        target_user_id=target_user_id,
        action=action,
    )
    return [AdminHistoryOut.model_validate(x) for x in items]

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status as http_status

from src.apps.users.di import get_users_service
from src.apps.users.schemas.pydantic.users import BanInfo, PaginatedUsersResponse, User
from src.apps.users.services.users import UserService
from src.core.db.models import Users
from src.core.dependencies.admin import require_admin
from src.core.dependencies.user import get_current_user_allow_banned

router = APIRouter(prefix="/users")


@router.get("/", status_code=http_status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def get_all_users(
    name: str | None = Query(default=None),
    is_banned: bool | None = Query(default=None),
    is_admin: bool | None = Query(default=None),
    sort_by: Literal["created_at", "updated_at"] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user_service: UserService = Depends(get_users_service),
) -> PaginatedUsersResponse:
    return await user_service.get_all_users(
        name=name,
        is_banned=is_banned,
        is_admin=is_admin,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page,
    )


@router.post("/", status_code=http_status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_user(user: User, user_service: UserService = Depends(get_users_service)) -> User:
    created = await user_service.create_user(user.model_dump())
    return User.model_validate(created)


@router.delete(
    "/{user_id}", status_code=http_status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)]
)
async def delete_user(
    user_id: UUID, user_service: UserService = Depends(get_users_service)
) -> None:
    await user_service.delete_user(user_id)
    return None


@router.get("/ban", response_model=BanInfo, status_code=http_status.HTTP_200_OK)
async def get_my_ban_info(
    current_user: Users = Depends(get_current_user_allow_banned),
    user_service: UserService = Depends(get_users_service),
) -> BanInfo:
    return await user_service.get_my_ban_info(current_user.id)

from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status as http_status

from src.core.dependencies.user import get_current_user_id

from ....di import get_users_service
from ....schemas.pydantic.users import User
from ....services.users import UserService

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(get_current_user_id)],
)


@router.get("/", status_code=http_status.HTTP_200_OK)
async def get_all_users(
    user_service: UserService = Depends(get_users_service),
) -> list[User]:
    users = await user_service.get_all_users()
    return [User.model_validate(u) for u in users]


@router.post("/", status_code=http_status.HTTP_201_CREATED)
async def create_user(
    user: User,
    user_service: UserService = Depends(get_users_service),
) -> User:
    created = await user_service.create_user(user.model_dump())
    return User.model_validate(created)


@router.delete("/{user_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_users_service),
) -> None:
    await user_service.delete_user(user_id)
    return None

from fastapi import APIRouter
from starlette import status

from ....schemas.pydantic.admin import User


class Admin:
    __router: APIRouter = APIRouter(prefix="/auth")

    @property
    def get_router(self):
        return self.__router

    @__router.patch(path="/ban/{user_id}", status_code=status.HTTP_200_OK)
    async def ban_user(user_id: int) -> User:
        return "ok"

    @__router.patch(path="/unban/{user_id}")
    async def unban_user(user_id: int) -> User:
        return "ok"

    @__router.patch(path="/edit/{user_id}")
    async def edit_user(user: User) -> User:
        return "ok"


admin = Admin()

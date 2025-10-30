from fastapi import APIRouter
from starlette import status as http_status

from ....schemas.pydantic.users import User


class Users:
    __router: APIRouter = APIRouter(prefix="/users", tags=["Users"])

    @property
    def get_router(self) -> APIRouter:
        return self.__router

    @__router.get(path="/", status_code=http_status.HTTP_200_OK)
    async def get_all_users() -> list[User]:
        return "ok"

    @__router.post(path="/", status_code=http_status.HTTP_201_CREATED)
    async def create_user(user: User) -> User:
        return {"status": "ok"}

    @__router.delete(path="/{user_id}", status_code=http_status.HTTP_204_NO_CONTENT)
    async def delete_user(user_id: int) -> None:
        return None


users = Users()

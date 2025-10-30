from fastapi import APIRouter
from starlette import status

from ....schemas.pydantic.notify import Notify


class Notify:
    __router: APIRouter = APIRouter(prefix="/notify")

    @property
    def get_router(self):
        return self.__router

    @__router.post(path="/bookings/{booking_id}", status_code=status.HTTP_200_OK)
    async def create_notify(notify: Notify) -> Notify:
        return "ok"

    @__router.delete(path="/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_notify(booking_id: int) -> None:
        return None

    @__router.delete(path="/bookings/", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_all() -> None:
        return None


notify = Notify()

from fastapi import APIRouter, Depends, Query
from starlette import status as http_status

from src.core.security import get_user_id_from_payload

from ....schemas.pydantic.booking import BookingCancel, BookingCreate, BookingRead


class Hint:
    __router: APIRouter = APIRouter(prefix="/bookings", tags=["Booking"])

    @property
    def get_router(self) -> APIRouter:
        return self.__router

    @__router.get(path="/me", status_code=http_status.HTTP_200_OK)
    async def get_my_booking(
        status_: str | None = Query(
            None, alias="status", description="Фильтр (active, cancelled, finished)"
        ),
        user_id: int = Depends(get_user_id_from_payload),
    ) -> list[BookingRead]:
        return "ok"

    @__router.post(path="/create", status_code=http_status.HTTP_201_CREATED)
    async def create_booking(booking: BookingCreate) -> BookingRead:
        return "ok"

    @__router.delete(path="/{booking_id}", status_code=http_status.HTTP_204_NO_CONTENT)
    async def delete_booking(booking: BookingCancel) -> None:
        return None


hint = Hint()

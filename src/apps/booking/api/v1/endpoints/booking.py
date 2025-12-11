from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status as http_status

from src.apps.mappers.booking import dc_to_pydantic
from src.core.dependencies.admin import require_admin
from src.core.dependencies.user import get_current_telegram_id, get_current_user_id

from ....di import get_booking_service
from ....schemas.pydantic.booking import BookingCreate, BookingRead, BookingType
from ....services.booking import BookingService

router = APIRouter(prefix="/bookings", dependencies=[Depends(get_current_user_id)])


@router.get("/me", status_code=http_status.HTTP_200_OK)
async def get_my_booking(
    user_id: UUID = Depends(get_current_user_id),
    booking: BookingService = Depends(get_booking_service),
) -> list[BookingRead]:
    bookings = await booking.get_my_active(user_id=user_id)
    return [dc_to_pydantic(b) for b in bookings]


@router.get("/history", status_code=http_status.HTTP_200_OK)
async def get_my_history(
    user_id: UUID = Depends(get_current_user_id),
    booking: BookingService = Depends(get_booking_service),
) -> list[BookingRead]:
    bookings = await booking.find_user(user_id=user_id)
    return [dc_to_pydantic(b) for b in bookings]


@router.get("/overlaps")
async def find_overlaps_endpoint(
    floor: int = Query(...),
    cso: int = Query(...),
    booking_type: BookingType = Query(..., alias="type"),
    starts_at: datetime = Query(...),
    ends_at: datetime = Query(...),
    booking: BookingService = Depends(get_booking_service),
):
    places = await booking.find_overlaps(
        floor=floor, cso=cso, booking_type=booking_type, starts_at=starts_at, ends_at=ends_at
    )
    return places


@router.post("/create", status_code=http_status.HTTP_201_CREATED)
async def create_booking(
    booking_create: BookingCreate,
    booking: BookingService = Depends(get_booking_service),
    user_id: UUID = Depends(get_current_user_id),
    telegram_user_id: int | None = Depends(get_current_telegram_id),
) -> BookingRead:
    created = await booking.create(
        booking_in=booking_create, user_id=user_id, telegram_user_id=telegram_user_id
    )
    return dc_to_pydantic(created)


@router.get("/available-starts", status_code=http_status.HTTP_200_OK)
async def get_available_starts(
    floor: int = Query(...),
    cso: int = Query(...),
    booking_type: BookingType = Query(..., alias="type"),
    from_time: datetime = Query(..., alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    booking: BookingService = Depends(get_booking_service),
) -> list[datetime]:
    if to_time is None:
        to_time = from_time + timedelta(days=2)

    starts = await booking.get_available_starts(
        floor=floor, booking_type=booking_type, from_time=from_time, cso=cso, to_time=to_time
    )
    return starts


@router.get("/available-ends", status_code=http_status.HTTP_200_OK)
async def get_available_ends(
    floor: int = Query(...),
    cso: int = Query(...),
    booking_type: BookingType = Query(..., alias="type"),
    start: datetime = Query(..., alias="start"),
    booking: BookingService = Depends(get_booking_service),
    end_date: datetime = Query(..., alias="end"),
) -> list[datetime]:
    ends = await booking.get_available_ends(
        floor=floor, booking_type=booking_type, cso=cso, start=start, end_date=end_date
    )
    return ends


@router.delete("/{booking_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: UUID,
    booking: BookingService = Depends(get_booking_service),
    current_user_id: UUID = Depends(get_current_user_id),
    is_admin: bool = Depends(require_admin),
) -> None:
    booking_deleted = await booking.delete_booking(booking_id, current_user_id, is_admin)
    return booking_deleted


@router.patch("/{booking_id}", status_code=http_status.HTTP_200_OK)
async def cancel_booking(
    booking_id: UUID,
    booking: BookingService = Depends(get_booking_service),
    current_user_id: UUID = Depends(get_current_user_id),
    is_admin: bool = Depends(require_admin),
) -> BookingRead:
    booking_canceled = await booking.booking_cancel(booking_id, current_user_id, is_admin)
    return booking_canceled


@router.get("/user/{user_id}", status_code=http_status.HTTP_200_OK)
async def find_user_booking(
    user_id: UUID,
    booking: BookingService = Depends(get_booking_service),
    admin=Depends(require_admin),
) -> list[BookingRead]:
    bookings = await booking.find_user(user_id)
    return [dc_to_pydantic(b) for b in bookings]

from fastapi import Depends

from src.apps.booking.repositories.sql.booking import BookingRepo
from src.apps.booking.services.booking import BookingService
from src.core.db.uow import UoW
from src.core.dependencies.db import get_uow


def get_booking_service(uow: UoW = Depends(get_uow)) -> BookingService:

    booking_repo = BookingRepo(uow.session)
    return BookingService(booking_repo=booking_repo, uow=uow)

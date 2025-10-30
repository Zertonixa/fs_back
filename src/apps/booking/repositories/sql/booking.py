from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models.booking import Booking

from ...schemas.dataclasses import BookingType
from ..interfaces import IBookingRepo


class BookingRepo(IBookingRepo):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, booking: BookingType) -> Booking:

        orm_obj = Booking(
            user_id=booking.user_id,
            machine_id=booking.machine_id,
            type=booking.type,
            status=booking.status,
            ends_at=booking.ends_at,
        )
        self.session.add(orm_obj)
        await self.session.flush()
        return BookingType.from_orm(orm_obj)

    async def get_by_id(self, booking_id):
        return await super().get_by_id(booking_id)

    async def find_overlaps(
        self, starts_time: datetime, ends_time: datetime
    ) -> list[UUID]:
        stmt = select(Booking.machine_id).where(
            and_(Booking.starts_at < starts_time, Booking.ends_at > ends_time)
        )
        result = await self.session.scalars(stmt)
        return list(result)

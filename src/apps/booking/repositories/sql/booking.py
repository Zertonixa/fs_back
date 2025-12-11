from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.mappers.booking import dc_to_orm, orm_to_dc
from src.core.db.models.booking import Booking as BookingORM
from src.core.db.models.booking import BookingType
from src.core.db.models.booking_slot import BookingSlots
from src.core.db.models.slot import Slot
from src.core.db.models.slot import Type as SlotType

from ...schemas.dataclasses.booking import Booking as BookingDC
from ...schemas.dataclasses.booking import BookingStatus
from ..interfaces import IBookingRepo

MIN_SLOT_DURATION = timedelta(minutes=30)
MAX_BOOKING_DURATION = timedelta(days=2)


class BookingRepo(IBookingRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, booking: BookingDC) -> BookingDC:
        orm_obj = dc_to_orm(booking)
        await orm_obj.save(self.session, refresh=True)

        if booking.slot_ids:
            slots = list(
                await self.session.scalars(select(Slot).where(Slot.id.in_(booking.slot_ids)))
            )
            orm_obj.slots = slots
            await orm_obj.save(self.session, refresh=True)

        return orm_to_dc(orm_obj)

    async def get_by_id(self, booking_id: UUID) -> BookingDC | None:
        obj = await BookingORM.get_by_id(self.session, booking_id)
        return orm_to_dc(obj) if obj else None

    async def find_user(self, user_id: UUID) -> list[BookingDC]:
        rows = await self.session.scalars(
            select(BookingORM).where(BookingORM.user_id == user_id)

        )
        return [orm_to_dc(obj) for obj in rows]

    async def get_my_active(self, user_id: UUID) -> list[BookingDC]:
        rows = await self.session.scalars(
            select(BookingORM).where(BookingORM.user_id == user_id, BookingORM.status == "NEW")
        )
        return [orm_to_dc(obj) for obj in rows]

    async def delete(self, booking_id: UUID) -> BookingDC | None:
        obj = await self.session.get(BookingORM, booking_id)
        if obj:
            await obj.delete(self.session)
        return orm_to_dc(obj)

    async def cancel(self, booking_ids: UUID) -> list[BookingDC]:
        stmt = select(BookingORM).where(BookingORM.id.in_(booking_ids))
        result = await self.session.execute(stmt)
        bookings = result.scalars().all()
        
        if not bookings:
            return []
        
        for booking in bookings:
            booking.status = "CANCELLED"
        
        await self.session.flush()
        
        return [orm_to_dc(booking) for booking in bookings]

    async def check_time(
        self,
        slot_ids: list[UUID],
        booking_type: BookingType,
        starts_at: datetime,
        ends_at: datetime,
    ) -> bool:
        if not slot_ids:
            return False
        stmt = (
            select(BookingORM.id)
            .join(BookingSlots, BookingSlots.booking_id == BookingORM.id)
            .where(
                BookingSlots.slot_id.in_(slot_ids),
                BookingORM.status != "CANCELLED",
                BookingORM.starts_at < ends_at,
                BookingORM.ends_at > starts_at,
            )
            .limit(1)
        )

        result = await self.session.scalars(stmt)
        return result.first() is not None

    async def save(self, booking: BookingDC) -> None:
        orm_obj = await self.session.get(BookingORM, booking.id)
        if not orm_obj:
            return

        orm_obj.user_id = booking.user_id
        orm_obj.type = booking.type
        orm_obj.starts_at = booking.starts_at
        orm_obj.ends_at = booking.ends_at
        orm_obj.status = booking.status

        slots: list[Slot] = []
        if booking.slot_ids:
            slots = list(
                await self.session.scalars(select(Slot).where(Slot.id.in_(booking.slot_ids)))
            )
        orm_obj.slots = slots

        await orm_obj.save(self.session, refresh=False)

    @staticmethod
    def _ceil_to_step(dt: datetime) -> datetime:
        minutes = (dt.minute // 15) * 15
        if dt.minute % 15 != 0:
            minutes += 15
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)

    @staticmethod
    def _floor_to_step(dt: datetime) -> datetime:
        minutes = (dt.minute // 15) * 15
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)

    async def _get_slot_ids(self, floor: int, cso: int, booking_type: BookingType) -> list[UUID]:
        slot_type = SlotType[booking_type]

        result = await self.session.scalars(
            select(Slot.id).where(
                Slot.floor == floor, Slot.cso == cso, Slot.type == slot_type, Slot.status.is_(True)
            )
        )
        return list(result)

    async def find_overlaps(
        self,
        floor: int,
        cso: int,
        booking_type: BookingType,
        starts_at: datetime,
        ends_at: datetime,
    ) -> list[list[dict[str, Any]]]:
        slot_type = SlotType[booking_type]

        slots_result = await self.session.execute(
            select(Slot.id, Slot.place, Slot.row)
            .where(Slot.floor == floor)
            .where(Slot.cso == cso)
            .where(Slot.type == slot_type)
            .where(Slot.status.is_(True))
            .order_by(Slot.row, Slot.place)
        )
        slots = slots_result.all()
        if not slots:
            return []

        slot_ids = [row[0] for row in slots]

        busy_result = await self.session.scalars(
            select(BookingSlots.slot_id)
            .join(BookingORM, BookingSlots.booking_id == BookingORM.id)
            .where(BookingSlots.slot_id.in_(slot_ids))
            .where(BookingORM.status == "NEW")
            .where(BookingORM.starts_at < ends_at)
            .where(BookingORM.ends_at > starts_at)
            .distinct()
        )
        busy_ids = set(busy_result)

        rows_map: dict[int, list[dict[str, Any]]] = defaultdict(list)

        for slot_id, place, row in slots:
            rows_map[row].append(
                {"id": slot_id, "place": place, "isAvailable": slot_id not in busy_ids}
            )

        return [rows_map[r] for r in sorted(rows_map.keys())]

    async def get_available_starts(
        self,
        floor: int,
        cso: int,
        booking_type: BookingType,
        from_time: datetime,
        to_time: datetime,
    ) -> list[datetime]:
        from_time = self._ceil_to_step(from_time)
        to_time = self._floor_to_step(min(to_time, from_time + MAX_BOOKING_DURATION))
        if from_time >= to_time:
            return []

        slot_ids = await self._get_slot_ids(floor, cso, booking_type)
        if not slot_ids:
            return []

        total_machines = len(slot_ids)

        booking_table = BookingORM.__tablename__
        booking_slots_table = BookingSlots.__tablename__

        sql = text(
            f"""
            WITH series AS (
                SELECT generate_series(
                    CAST(:from_time AS timestamptz),
                    CAST(:to_time AS timestamptz) - INTERVAL '15 minutes',
                    INTERVAL '15 minutes'
                ) AS slot_time
            )
            SELECT s.slot_time
            FROM series s
            LEFT JOIN {booking_table} b
              ON b.type = :booking_type
             AND b.status != :cancelled_status
             AND b.starts_at < s.slot_time + INTERVAL '15 minutes'
             AND b.ends_at > s.slot_time
            LEFT JOIN {booking_slots_table} bs
              ON bs.booking_id = b.id
             AND bs.slot_id = ANY(:slot_ids)
            GROUP BY s.slot_time
            HAVING COUNT(DISTINCT bs.slot_id) < :total_machines
            ORDER BY s.slot_time;
        """
        )

        rows = await self.session.execute(
            sql,
            {
                "from_time": from_time,
                "to_time": to_time,
                "slot_ids": slot_ids,
                "booking_type": booking_type,
                "cancelled_status": "CANCELLED",
                "total_machines": total_machines,
            },
        )

        return [row.slot_time for row in rows]

    async def get_available_ends(
        self,
        floor: int,
        cso: int,
        booking_type: BookingType,
        start: datetime,
        end_date: datetime | None = None,
    ) -> list[datetime]:
        start = self._ceil_to_step(start)

        if booking_type == BookingType.WASHING:
            max_duration = timedelta(hours=8)
        elif booking_type == BookingType.DRYING:
            max_duration = timedelta(days=2)
        else:
            max_duration = MAX_BOOKING_DURATION

        max_end_time = start + max_duration

        if end_date:
            end_date_start = datetime.combine(end_date.date(), datetime.min.time()).replace(
                tzinfo=start.tzinfo
            )
            end_date_end = datetime.combine(end_date.date(), datetime.min.time()).replace(
                hour=23, minute=30, second=0, tzinfo=start.tzinfo
            )

            end_limit = min(max_end_time, end_date_end)
        else:
            end_limit = self._floor_to_step(max_end_time)


        if end_limit <= start + timedelta(minutes=30):
            return []

        slot_ids = await self._get_slot_ids(floor, cso, booking_type)
        if not slot_ids:
            return []

        booking_table = BookingORM.__tablename__
        slot_table = Slot.__tablename__
        booking_slots_table = BookingSlots.__tablename__

        sql = text(
            f"""
            WITH ends AS (
                SELECT generate_series(
                    CAST(:start AS timestamptz) + INTERVAL '30 minutes',
                    CAST(:end_limit AS timestamptz),
                    INTERVAL '30 minutes'
                ) AS end_time
            ),
            available_slots AS (
                SELECT s.id as slot_id, e.end_time
                FROM {slot_table} s
                CROSS JOIN ends e
                WHERE s.id = ANY(:slot_ids)
            )
            SELECT DISTINCT av.end_time  -- DISTINCT вместо GROUP BY/HAVING
            FROM available_slots av
            WHERE NOT EXISTS (
                SELECT 1
                FROM {booking_table} b
                JOIN {booking_slots_table} bs ON bs.booking_id = b.id
                WHERE bs.slot_id = av.slot_id
                AND b.type = :booking_type
                AND b.status != :cancelled_status
                AND b.starts_at < av.end_time
                AND b.ends_at > :start
            )
            ORDER BY av.end_time;
            """
        )

        rows = await self.session.execute(
            sql,
            {
                "start": start,
                "end_limit": end_limit,
                "slot_ids": slot_ids,
                "booking_type": booking_type,
                "cancelled_status": "CANCELLED",
                "total_slots": len(slot_ids),
            },
        )

        return [row.end_time for row in rows]

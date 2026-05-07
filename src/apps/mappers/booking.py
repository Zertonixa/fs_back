# src/mappers/booking.py
from uuid import UUID

from src.apps.booking.schemas.dataclasses.booking import Booking as BookingDC
from src.apps.booking.schemas.dataclasses.booking import BookingCreate
from src.apps.booking.schemas.pydantic.booking import BookingRead
from src.core.db.models.booking import Booking as BookingORM


def orm_to_dc(orm: BookingORM) -> BookingDC:
    return BookingDC(
        id=orm.id,
        user_id=orm.user_id,
        slot_ids=[slot.id for slot in orm.slots],
        slot_places=[slot.place for slot in orm.slots],
        floor=orm.slots[0].floor if orm.slots else None,
        start_reminder_task_id=orm.start_reminder_task_id,
        end_reminder_task_id=orm.end_reminder_task_id,
        complete_task_id=orm.complete_task_id,
        type=orm.type,
        starts_at=orm.starts_at,
        ends_at=orm.ends_at,
        status=orm.status,
    )


def dc_to_orm(dc: BookingDC) -> BookingORM:
    return BookingORM(
        id=dc.id,
        user_id=dc.user_id,
        start_reminder_task_id=dc.start_reminder_task_id,
        end_reminder_task_id=dc.end_reminder_task_id,
        complete_task_id=dc.complete_task_id,
        type=dc.type,
        starts_at=dc.starts_at,
        ends_at=dc.ends_at,
        status=dc.status,
    )


def dc_to_pydantic(dc: BookingDC) -> BookingRead:
    return BookingRead(
        id=dc.id,
        user_id=dc.user_id,
        type=dc.type,
        floor=dc.floor,
        starts_at=dc.starts_at,
        ends_at=dc.ends_at,
        status=dc.status,
        slot_ids=dc.slot_ids,
        slot_places=dc.slot_places,
    )


def create_to_dc(dc: BookingCreate, user_id: UUID) -> BookingDC:
    return BookingDC(
        id=None,
        user_id=user_id,
        type=dc.type,
        floor=dc.floor,
        starts_at=dc.starts_at,
        ends_at=dc.ends_at,
        status="NEW",
        slot_ids=dc.slot_ids,
        start_reminder_task_id=None,
        end_reminder_task_id=None,
        complete_task_id=None,
    )

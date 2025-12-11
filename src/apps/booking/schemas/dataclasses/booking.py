from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from uuid import UUID

BookingStatus = Literal["NEW", "CANCELLED", "DONE"]
BookingType = Literal["WASHING", "DRYING"]


@dataclass(slots=True)
class Booking:
    id: UUID
    user_id: UUID
    type: BookingType
    start_reminder_task_id: str | None
    end_reminder_task_id: str | None
    complete_task_id: str | None
    starts_at: datetime
    floor: int | None
    ends_at: datetime
    status: BookingStatus = "NEW"
    slot_places: list[int] = field(default_factory=list)
    slot_ids: list[UUID] = field(default_factory=list)


@dataclass(slots=True)
class BookingCreate:
    user_id: UUID
    type: BookingType
    starts_at: datetime
    floor: int
    ends_at: datetime
    slot_ids: list[UUID]

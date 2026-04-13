from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

BookingStatus = Literal["NEW", "CANCELLED", "DONE"]
BookingType = Literal["WASHING", "DRYING"]


class BookingCreate(BaseModel):
    type: BookingType
    starts_at: datetime
    ends_at: datetime
    floor: int
    slot_ids: list[UUID]


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    type: BookingType
    slot_ids: list[UUID]
    slot_places: list[int]
    floor: int | None
    starts_at: datetime
    ends_at: datetime
    status: BookingStatus = "NEW"


class BookingCancel(BaseModel):
    slot_id: int


class BookingTime(BaseModel):
    time: datetime


class BookingNearest(BaseModel):
    starts_at: datetime
    ends_at: datetime
    slot_id: UUID
    slot_place: int
    floor: int

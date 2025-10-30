from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

BookingStatus = Literal["NEW", "CANCELLED", "DONE"]
BookingType = Literal["WASHING", "DRYING"]


class BookingCreate(BaseModel):
    machine_id: UUID
    starts_at: datetime
    ends_at: datetime


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    type: BookingType
    machine_id: UUID
    starts_at: datetime
    ends_at: datetime
    status: BookingStatus = "NEW"


class BookingCancel(BaseModel):
    reason: str | None = Field(default=None, max_length=200)
    slot_id: int

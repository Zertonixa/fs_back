from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

Status = Literal["NEW", "CANCELLED", "DONE"]
BookingType = Literal["WASHING", "DRYING"]


@dataclass(slots=True)
class Booking:
    id: UUID
    user_id: UUID
    machine_id: UUID
    type: BookingType
    starts_at: datetime
    ends_at: datetime
    status: BookingType = "New"

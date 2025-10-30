from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

SlotType = Literal["WASHING", "DRYING"]


class Device(BaseModel):
    id: UUID
    type: SlotType
    floor: int
    place: int
    status: bool
    created_at: datetime
    updated_at: datetime

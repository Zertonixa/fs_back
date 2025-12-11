from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

SlotType = Literal["WASHING", "DRYING"]


class Slot(BaseModel):
    id: UUID
    type: SlotType
    floor: int
    place: int
    status: bool
    created_at: datetime
    updated_at: datetime


class SlotCreate(BaseModel):
    type: SlotType
    floor: int
    place: int
    cso: int
    row: int
    status: bool = True


class SlotUpdate(BaseModel):
    type: SlotType | None = None
    floor: int | None = None
    place: int | None = None
    status: bool | None = None


class SlotCell(BaseModel):
    id: UUID
    place: int
    is_available: bool

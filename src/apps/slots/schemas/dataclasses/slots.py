from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.core.db.models.slot import Type as SlotType


@dataclass(slots=True)
class Slot:
    id: UUID
    type: SlotType
    floor: int
    row: int
    place: int
    cso: int
    status: bool
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class SlotCreate:
    type: SlotType
    floor: int
    row: int
    place: int
    cso: int
    status: bool = True


@dataclass(slots=True)
class SlotUpdate:
    type: SlotType | None = None
    floor: int | None = None
    row: int | None = None
    place: int | None = None
    cso: int | None = None
    status: bool | None = None

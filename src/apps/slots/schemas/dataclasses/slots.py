from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.core.db.models.slot import Type as SlotType


@dataclass
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

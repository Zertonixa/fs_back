from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

SlotType = Literal["WASHING", "DRYING"]


class Notify(BaseModel):
    id: UUID
    user_id: int
    starts_at: datetime
    ends_at: datetime

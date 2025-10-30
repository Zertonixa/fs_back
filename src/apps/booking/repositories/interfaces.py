from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from ..schemas.dataclasses.booking import Booking


class IBookingRepo(ABC):
    @abstractmethod
    async def create(self, booking: Booking) -> "Booking": ...

    @abstractmethod
    async def get_by_id(self, booking_id: UUID) -> "Booking" | None: ...

    @abstractmethod
    async def find_overlaps(
        self, machine_id: UUID, starts_at: datetime, ends_at: datetime
    ) -> Sequence[UUID]: ...

    @abstractmethod
    async def find_user(self, user_id: UUID) -> Sequence["Booking"]: ...

    @abstractmethod
    async def save(self, booking: Booking) -> None: ...

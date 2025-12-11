from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from typing import Any
from uuid import UUID

from src.core.db.models.booking import BookingType

from ..schemas.dataclasses.booking import Booking


class IBookingRepo(ABC):
    @abstractmethod
    async def create(self, booking: Booking) -> Booking: ...

    @abstractmethod
    async def get_by_id(self, booking_id: UUID) -> Booking | None: ...

    @abstractmethod
    async def find_overlaps(
        self,
        cso: int,
        floor: int,
        booking_type: BookingType,
        starts_at: datetime,
        ends_at: datetime,
    ) -> list[list[dict[str, Any]]]: ...

    @abstractmethod
    async def get_my_active(self, user_id: UUID) -> Sequence[Booking]: ...

    @abstractmethod
    async def check_time(
        self,
        slot_ids: list[UUID],
        booking_type: BookingType,
        starts_at: datetime,
        ends_at: datetime,
    ) -> bool: ...

    @abstractmethod
    async def delete(self, booking_id: UUID) -> Booking | None: ...

    @abstractmethod
    async def cancel(self, booking_id: UUID) -> Booking | None: ...

    @abstractmethod
    async def find_user(self, user_id: UUID) -> Sequence[Booking]: ...

    @abstractmethod
    async def save(self, booking: Booking) -> None: ...

    @abstractmethod
    async def get_available_starts(
        self,
        floor: int,
        cso: int,
        booking_type: BookingType,
        from_time: datetime,
        to_time: datetime,
    ) -> list[datetime]: ...

    @abstractmethod
    async def get_available_ends(
        self,
        floor: int,
        cso: int,
        booking_type: BookingType,
        start: datetime,
        end_date: datetime | None = None,
    ) -> list[datetime]: ...

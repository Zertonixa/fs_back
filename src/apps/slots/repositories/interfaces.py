from abc import ABC, abstractmethod
from uuid import UUID

from src.core.db.models.slot import Type as SlotType

from ..schemas.dataclasses.slots import Slot


class ISlotRepo(ABC):
    @abstractmethod
    async def get_all(
        self,
        type_: SlotType | None = None,
        floor_: int | None = None,
        cso_: int | None = None,
    ) -> list[Slot]: ...

    @abstractmethod
    async def get_by_id(self, slot_id: UUID) -> Slot | None: ...

    @abstractmethod
    async def create(self, slot: Slot) -> Slot: ...

    @abstractmethod
    async def update(self, slot_id: UUID, slot: Slot) -> Slot | None: ...

    @abstractmethod
    async def delete(self, slot_id: UUID) -> None: ...

    @abstractmethod
    async def get_by_params(
        self,
        type_: SlotType,
        floor_: int,
        cso_: int,
        row_: int,
        place_: int,
    ) -> Slot | None: ...

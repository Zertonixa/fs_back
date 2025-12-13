from collections import defaultdict
from uuid import UUID

from fastapi import HTTPException, status

from src.apps.slots.repositories.interfaces import ISlotRepo
from src.apps.slots.schemas.dataclasses.slots import Slot as SlotDC
from src.apps.slots.schemas.pydantic.slots import SlotCell
from src.core.db.models.slot import Type as SlotType
from src.core.db.uow import UoW


class SlotService:
    def __init__(self, slot_repo: ISlotRepo, uow: UoW):
        self.slot_repo = slot_repo
        self.uow = uow

    async def _get_or_404(self, slot_id: UUID) -> SlotDC:
        slot = await self.slot_repo.get_by_id(slot_id)
        if slot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="slot not found")
        return slot

    async def get_flat(
        self, type_: SlotType | None = None, floor_: int | None = None, cso_: int | None = None
    ) -> list[SlotDC]:
        return await self.slot_repo.get_all(type_, floor_, cso_)

    async def get_matrix(
        self, type_: SlotType | None = None, floor_: int | None = None, cso_: int | None = None
    ) -> list[list[SlotCell]]:
        slots = await self.slot_repo.get_all(type_, floor_, cso_)

        if not slots:
            return []

        matrix_raw: dict[int, list[SlotCell]] = defaultdict(list)

        for s in slots:
            matrix_raw[s.row].append(SlotCell(place=s.place, id=s.id, is_available=s.status))

        matrix: list[list[SlotCell]] = [
            matrix_raw[row_index] for row_index in sorted(matrix_raw.keys())
        ]
        return matrix

    async def get_by_id(self, slot_id: UUID) -> SlotDC | None:
        return await self._get_or_404(slot_id)

    async def create(self, slot: SlotDC) -> SlotDC:
        async with self.uow.transaction():
            existing = await self.slot_repo.get_by_params(
                type_=slot.type, floor_=slot.floor, cso_=slot.cso, row_=slot.row, place_=slot.place
            )
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="slot with same params already exists",
                )

            return await self.slot_repo.create(slot)

    async def update(self, slot_id: UUID, slot: SlotDC) -> SlotDC:
        async with self.uow.transaction():
            await self._get_or_404(slot_id)

            existing = await self.slot_repo.get_by_params(
                type_=slot.type, floor_=slot.floor, cso_=slot.cso, row_=slot.row, place_=slot.place
            )
            if existing is not None and existing.id != slot_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="slot with same params already exists",
                )

            updated = await self.slot_repo.update(slot_id, slot)
            if updated is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="slot not found")
            return updated

    async def delete(self, slot_id: UUID) -> None:
        async with self.uow.transaction():
            await self._get_or_404(slot_id)
            await self.slot_repo.delete(slot_id)

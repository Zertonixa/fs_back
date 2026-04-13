from collections import defaultdict
from uuid import UUID

from fastapi import HTTPException, status

from src.apps.admin.events import AdminActionEvent
from src.apps.booking.repositories.interfaces import IBookingRepo
from src.apps.slots.repositories.interfaces import ISlotRepo
from src.apps.slots.schemas.dataclasses.slots import Slot as SlotDC
from src.apps.slots.schemas.dataclasses.slots import SlotCreate as SlotCreateDC
from src.apps.slots.schemas.dataclasses.slots import SlotUpdate as SlotUpdateDC
from src.apps.slots.schemas.pydantic.slots import SlotCell
from src.core.db.models.admin_history import AdminAction
from src.core.db.models.slot import Type as SlotType
from src.core.db.uow import UoW


class SlotService:
    def __init__(self, slot_repo: ISlotRepo, booking_repo: IBookingRepo, uow: UoW):
        self.slot_repo = slot_repo
        self.booking_repo = booking_repo
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
            matrix_raw[s.row].append(
                SlotCell(place=s.place, id=s.id, is_available=s.status, raw=s.row, floor=s.floor)
            )

        return [matrix_raw[row_index] for row_index in sorted(matrix_raw.keys())]

    async def get_by_id(self, slot_id: UUID) -> SlotDC | None:
        return await self._get_or_404(slot_id)

    async def create(self, slot: SlotCreateDC, *, moderator_id: UUID) -> SlotDC:
        async with self.uow.transaction():
            existing = await self.slot_repo.get_by_params(
                type_=slot.type, floor_=slot.floor, cso_=slot.cso, row_=slot.row, place_=slot.place
            )
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="slot with same params already exists",
                )

            created = await self.slot_repo.create(slot)

            self.uow.add_event(
                AdminActionEvent(
                    moderator_id=moderator_id,
                    action=AdminAction.CHANGE_SLOT,
                    description=f"Created slot {created.id}",
                    slot_id=created.id,
                )
            )

            return created

    async def update(self, slot_id: UUID, patch: SlotUpdateDC, *, moderator_id: UUID) -> SlotDC:
        async with self.uow.transaction():
            current = await self._get_or_404(slot_id)

            new_type = patch.type if patch.type is not None else current.type
            new_floor = patch.floor if patch.floor is not None else current.floor
            new_cso = patch.cso if patch.cso is not None else current.cso
            new_row = patch.row if patch.row is not None else current.row
            new_place = patch.place if patch.place is not None else current.place

            existing = await self.slot_repo.get_by_params(
                type_=new_type, floor_=new_floor, cso_=new_cso, row_=new_row, place_=new_place
            )
            if existing is not None and existing.id != slot_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="slot with same params already exists",
                )

            updated = await self.slot_repo.update(slot_id, patch)
            if updated is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="slot not found")

            cancelled = await self.booking_repo.cancel_all_by_slot(slot_id)

            self.uow.add_event(
                AdminActionEvent(
                    moderator_id=moderator_id,
                    action=AdminAction.CHANGE_SLOT,
                    description=f"Updated slot {slot_id}",
                    slot_id=slot_id,
                )
            )

            return updated

    async def delete(self, slot_id: UUID, *, moderator_id: UUID) -> None:
        async with self.uow.transaction():
            await self._get_or_404(slot_id)
            await self.slot_repo.delete(slot_id)

            self.uow.add_event(
                AdminActionEvent(
                    moderator_id=moderator_id,
                    action=AdminAction.CHANGE_SLOT,
                    description=f"Deleted slot {slot_id}",
                )
            )

    async def toggle_status(self, slot_id: UUID, *, moderator_id: UUID) -> SlotDC:
        async with self.uow.transaction():
            current = await self._get_or_404(slot_id)

            patch = SlotUpdateDC(status=not current.status)

            updated = await self.slot_repo.update(slot_id, patch)
            if updated is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="slot not found")

            cancelled = await self.booking_repo.cancel_all_by_slot(slot_id)

            self.uow.add_event(
                AdminActionEvent(
                    moderator_id=moderator_id,
                    action=AdminAction.CHANGE_SLOT,
                    description=(
                        f"Toggled slot {slot_id} status to {updated.status}. "
                        f"Cancelled bookings: {cancelled}"
                    ),
                    slot_id=slot_id,
                )
            )

            return updated

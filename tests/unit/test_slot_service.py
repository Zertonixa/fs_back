from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import pytest

from src.apps.slots.schemas.dataclasses.slots import Slot, SlotUpdate
from src.apps.slots.services.slots import SlotService
from src.core.db.models.admin_history import AdminAction
from src.core.db.models.slot import Type


class FakeSlotRepo:
    def __init__(self, slots: list[Slot]) -> None:
        self.slots = {slot.id: slot for slot in slots}

    async def get_all(self, type_=None, floor_=None, cso_=None):
        return list(self.slots.values())

    async def get_by_id(self, slot_id):
        return self.slots.get(slot_id)

    async def update(self, slot_id, patch: SlotUpdate):
        slot = self.slots[slot_id]
        updated = Slot(
            id=slot.id,
            type=patch.type if patch.type is not None else slot.type,
            floor=patch.floor if patch.floor is not None else slot.floor,
            row=patch.row if patch.row is not None else slot.row,
            place=patch.place if patch.place is not None else slot.place,
            cso=patch.cso if patch.cso is not None else slot.cso,
            status=patch.status if patch.status is not None else slot.status,
            created_at=slot.created_at,
            updated_at=slot.updated_at,
        )
        self.slots[slot_id] = updated
        return updated


class FakeBookingRepo:
    def __init__(self) -> None:
        self.cancelled_slots = []

    async def cancel_all_by_slot(self, slot_id):
        self.cancelled_slots.append(slot_id)
        return 2


class FakeUoW:
    def __init__(self) -> None:
        self.events = []

    @asynccontextmanager
    async def transaction(self):
        yield self

    def add_event(self, event) -> None:
        self.events.append(event)


def make_slot(row: int, place: int, *, available: bool = True) -> Slot:
    now = datetime.now(UTC)
    return Slot(
        id=uuid.uuid4(),
        type=Type.WASHING,
        floor=1,
        row=row,
        place=place,
        cso=4,
        status=available,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.anyio
async def test_get_matrix_groups_slots_by_row() -> None:
    slots = [make_slot(2, 3), make_slot(1, 1), make_slot(2, 1)]
    service = SlotService(FakeSlotRepo(slots), FakeBookingRepo(), FakeUoW())

    matrix = await service.get_matrix(Type.WASHING, 1, 4)

    assert len(matrix) == 2
    assert [cell.raw for cell in matrix[0]] == [1]
    assert sorted(cell.place for cell in matrix[1]) == [1, 3]


@pytest.mark.anyio
async def test_toggle_status_cancels_bookings_and_emits_admin_event() -> None:
    slot = make_slot(1, 1, available=True)
    booking_repo = FakeBookingRepo()
    uow = FakeUoW()
    service = SlotService(FakeSlotRepo([slot]), booking_repo, uow)

    updated = await service.toggle_status(slot.id, moderator_id=uuid.uuid4())

    assert updated.status is False
    assert booking_repo.cancelled_slots == [slot.id]
    assert len(uow.events) == 1
    assert uow.events[0].action == AdminAction.CHANGE_SLOT
    assert str(slot.id) in uow.events[0].description

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from src.apps.booking.schemas.dataclasses.booking import Booking, BookingCreate
from src.apps.booking.services.booking import BookingService


class FakeBookingRepo:
    def __init__(self, *, has_conflict: bool = False) -> None:
        self.has_conflict = has_conflict
        self.saved = []
        self.created = []

    async def check_time(self, **kwargs):
        return self.has_conflict

    async def create(self, booking: Booking) -> Booking:
        created = Booking(
            id=uuid.uuid4(),
            user_id=booking.user_id,
            type=booking.type,
            start_reminder_task_id=None,
            end_reminder_task_id=None,
            complete_task_id=None,
            starts_at=booking.starts_at,
            ends_at=booking.ends_at,
            floor=booking.floor,
            slot_ids=booking.slot_ids,
            slot_places=[1 for _ in booking.slot_ids],
            status=booking.status,
        )
        self.created.append(created)
        return created

    async def save(self, booking: Booking) -> None:
        self.saved.append(booking)

    async def get_by_id(self, booking_id):
        return None


class FakeUoW:
    def __init__(self) -> None:
        self.committed = 0
        self.rolled_back = 0

    @asynccontextmanager
    async def transaction(self):
        try:
            yield self
            self.committed += 1
        except Exception:
            self.rolled_back += 1
            raise


@pytest.mark.anyio
async def test_create_rejects_empty_slot_ids() -> None:
    repo = FakeBookingRepo()
    service = BookingService(repo, FakeUoW())

    with pytest.raises(HTTPException, match="slot_ids must not be empty"):
        await service.create(
            BookingCreate(
                user_id=uuid.uuid4(),
                type="WASHING",
                starts_at=datetime.now(UTC) + timedelta(hours=1),
                ends_at=datetime.now(UTC) + timedelta(hours=2),
                floor=1,
                slot_ids=[],
            ),
            user_id=uuid.uuid4(),
        )


@pytest.mark.anyio
async def test_create_rejects_conflicting_booking() -> None:
    repo = FakeBookingRepo(has_conflict=True)
    service = BookingService(repo, FakeUoW())

    with pytest.raises(HTTPException, match="slot is already booked"):
        await service.create(
            BookingCreate(
                user_id=uuid.uuid4(),
                type="WASHING",
                starts_at=datetime.now(UTC) + timedelta(hours=1),
                ends_at=datetime.now(UTC) + timedelta(hours=2),
                floor=1,
                slot_ids=[uuid.uuid4()],
            ),
            user_id=uuid.uuid4(),
        )


@pytest.mark.anyio
async def test_create_saves_generated_task_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    repo = FakeBookingRepo()
    service = BookingService(repo, FakeUoW())

    class DummyTask:
        def __init__(self, prefix: str) -> None:
            self.prefix = prefix
            self.calls = 0

        def apply_async(self, *args, **kwargs):
            self.calls += 1
            return SimpleNamespace(id=f"{self.prefix}-{self.calls}")

    monkeypatch.setattr(
        "src.apps.booking.services.booking.send_booking_reminder", DummyTask("start")
    )
    monkeypatch.setattr(
        "src.apps.booking.services.booking.send_booking_end_reminder", DummyTask("end")
    )
    monkeypatch.setattr("src.apps.booking.services.booking.complete_booking", DummyTask("done"))

    created = await service.create(
        BookingCreate(
            user_id=uuid.uuid4(),
            type="WASHING",
            starts_at=datetime.now(UTC) + timedelta(hours=1),
            ends_at=datetime.now(UTC) + timedelta(hours=2),
            floor=1,
            slot_ids=[uuid.uuid4()],
        ),
        user_id=uuid.uuid4(),
        telegram_user_id=123456,
    )

    assert created.start_reminder_task_id == "start-1"
    assert created.end_reminder_task_id == "end-1"
    assert created.complete_task_id == "done-1"
    assert repo.saved[-1].complete_task_id == "done-1"

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from src.core.db.models.booking import Booking as BookingORM
from src.core.db.models.booking_slot import BookingSlots

pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_create_booking_persists_row_and_returns_payload(
    client, db_helpers, db_session
) -> None:
    user = await db_helpers.create_user(telegram_id=2001, username="booker")
    slot = await db_helpers.create_slot(type_="WASHING", floor=1, cso=4, row=1, place=1)
    await db_helpers.auth_as(client, user)

    starts_at = datetime.now(UTC) + timedelta(hours=1)
    ends_at = starts_at + timedelta(hours=1)

    response = await client.post(
        "/api/v1/bookings/create",
        json={
            "type": "WASHING",
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
            "floor": 1,
            "slot_ids": [str(slot.id)],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "WASHING"
    assert body["floor"] == 1
    assert body["slot_places"] == [1]

    booking = await db_session.get(BookingORM, body["id"])
    assert booking is not None

    stmt = select(BookingSlots).where(
        BookingSlots.booking_id == booking.id, BookingSlots.slot_id == slot.id
    )
    link = (await db_session.execute(stmt)).scalar_one_or_none()
    assert link is not None


@pytest.mark.anyio
async def test_get_my_bookings_returns_only_active_rows(client, db_helpers) -> None:
    user = await db_helpers.create_user(telegram_id=2002, username="active-user")
    slot = await db_helpers.create_slot(type_="DRYING", floor=2, cso=4, row=1, place=7)
    now = datetime.now(UTC)

    await db_helpers.create_booking_row(
        user_id=user.id,
        slot_ids=[slot.id],
        type_="DRYING",
        starts_at=now + timedelta(hours=1),
        ends_at=now + timedelta(hours=3),
        status="NEW",
    )
    await db_helpers.create_booking_row(
        user_id=user.id,
        slot_ids=[slot.id],
        type_="DRYING",
        starts_at=now - timedelta(days=1),
        ends_at=now - timedelta(days=1) + timedelta(hours=1),
        status="DONE",
    )

    await db_helpers.auth_as(client, user)

    response = await client.get("/api/v1/bookings/me")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["status"] == "NEW"


@pytest.mark.anyio
async def test_get_booking_history_returns_all_user_rows(client, db_helpers) -> None:
    user = await db_helpers.create_user(telegram_id=2003, username="history-user")
    slot = await db_helpers.create_slot(type_="WASHING", floor=1, cso=4, row=1, place=2)
    now = datetime.now(UTC)

    await db_helpers.create_booking_row(
        user_id=user.id,
        slot_ids=[slot.id],
        type_="WASHING",
        starts_at=now + timedelta(hours=2),
        ends_at=now + timedelta(hours=3),
        status="NEW",
    )
    await db_helpers.create_booking_row(
        user_id=user.id,
        slot_ids=[slot.id],
        type_="WASHING",
        starts_at=now - timedelta(days=1),
        ends_at=now - timedelta(days=1) + timedelta(hours=1),
        status="DONE",
    )

    await db_helpers.auth_as(client, user)

    response = await client.get("/api/v1/bookings/history")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.anyio
async def test_admin_can_read_other_user_bookings(client, db_helpers) -> None:
    admin = await db_helpers.create_user(telegram_id=9001, username="admin", is_admin=True)
    user = await db_helpers.create_user(telegram_id=2004, username="target")
    slot = await db_helpers.create_slot(type_="WASHING", floor=1, cso=4, row=1, place=3)
    now = datetime.now(UTC)

    await db_helpers.create_booking_row(
        user_id=user.id,
        slot_ids=[slot.id],
        type_="WASHING",
        starts_at=now + timedelta(hours=2),
        ends_at=now + timedelta(hours=3),
        status="NEW",
    )

    await db_helpers.auth_as(client, admin)

    response = await client.get(f"/api/v1/bookings/user/{user.id}")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["user_id"] == str(user.id)


@pytest.mark.anyio
async def test_cancel_booking_changes_status(client, db_helpers, db_session) -> None:
    user = await db_helpers.create_user(telegram_id=2005, username="cancel-user")
    slot = await db_helpers.create_slot(type_="WASHING", floor=1, cso=4, row=1, place=4)
    now = datetime.now(UTC)

    booking = await db_helpers.create_booking_row(
        user_id=user.id,
        slot_ids=[slot.id],
        type_="WASHING",
        starts_at=now + timedelta(hours=1),
        ends_at=now + timedelta(hours=2),
        status="NEW",
    )

    await db_helpers.auth_as(client, user)

    response = await client.patch("/api/v1/bookings", json=[str(booking.id)])
    assert response.status_code == 200

    refreshed = await db_session.get(BookingORM, booking.id)
    assert refreshed.status.value == "CANCELLED"

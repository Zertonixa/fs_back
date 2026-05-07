from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

pytestmark = pytest.mark.e2e


@pytest.mark.anyio
async def test_create_read_cancel_booking_flow(client, db_helpers) -> None:
    user = await db_helpers.create_user(telegram_id=9601, username="flow-user")
    slot = await db_helpers.create_slot(type_="WASHING", floor=3, cso=4, row=1, place=11)
    await db_helpers.auth_as(client, user)

    starts_at = datetime.now(UTC) + timedelta(hours=2)
    ends_at = starts_at + timedelta(hours=1)

    create_response = await client.post(
        "/api/v1/bookings/create",
        json={
            "type": "WASHING",
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
            "floor": 3,
            "slot_ids": [str(slot.id)],
        },
    )
    assert create_response.status_code == 201
    booking_id = create_response.json()["id"]

    list_response = await client.get("/api/v1/bookings/me")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    cancel_response = await client.patch("/api/v1/bookings", json=[booking_id])
    assert cancel_response.status_code == 200

    active_after_cancel = await client.get("/api/v1/bookings/me")
    assert active_after_cancel.status_code == 200
    assert active_after_cancel.json() == []

    history_response = await client.get("/api/v1/bookings/history")
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1

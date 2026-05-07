from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_create_booking_rejects_invalid_slot_uuid(client, db_helpers) -> None:
    user = await db_helpers.create_user(telegram_id=9501, username="validator")
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
            "slot_ids": ["bad-uuid"],
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_available_starts_rejects_invalid_type(client) -> None:
    response = await client.get(
        "/api/v1/bookings/available-starts",
        params={"floor": 1, "cso": 4, "type": "INVALID", "from": datetime.now(UTC).isoformat()},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_users_list_rejects_invalid_page(client, db_helpers) -> None:
    admin = await db_helpers.create_user(telegram_id=9502, username="admin", is_admin=True)
    await db_helpers.auth_as(client, admin)

    response = await client.get("/api/v1/users/", params={"page": 0})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_my_complaints_rejects_limit_over_100(client, db_helpers) -> None:
    user = await db_helpers.create_user(telegram_id=9503, username="complainer")
    await db_helpers.auth_as(client, user)

    response = await client.get("/api/v1/complaints/me", params={"limit": 101})
    assert response.status_code == 422

from __future__ import annotations

import pytest

from src.core.db.models.slot import Slot as SlotORM

pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_get_all_slots_returns_matrix_from_db(client, db_helpers) -> None:
    await db_helpers.create_slot(type_="WASHING", floor=1, cso=4, row=1, place=1, status=True)
    await db_helpers.create_slot(type_="WASHING", floor=1, cso=4, row=1, place=2, status=False)
    await db_helpers.create_slot(type_="WASHING", floor=1, cso=4, row=2, place=1, status=True)

    response = await client.get(
        "/api/v1/slots/", params={"type": "WASHING", "floor_": 1, "cso_": 4}
    )
    assert response.status_code == 200
    matrix = response.json()
    assert len(matrix) == 2


@pytest.mark.anyio
async def test_admin_can_create_slot(client, db_helpers, db_session) -> None:
    admin = await db_helpers.create_user(telegram_id=9101, username="admin", is_admin=True)
    await db_helpers.auth_as(client, admin)

    response = await client.post(
        "/api/v1/slots/",
        json={"type": "DRYING", "floor": 3, "place": 5, "cso": 8, "row": 2, "status": True},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "DRYING"
    assert body["floor"] == 3

    slot = await db_session.get(SlotORM, body["id"])
    assert slot is not None


@pytest.mark.anyio
async def test_admin_can_update_toggle_and_delete_slot(client, db_helpers, db_session) -> None:
    admin = await db_helpers.create_user(telegram_id=9102, username="admin", is_admin=True)
    slot = await db_helpers.create_slot(
        type_="WASHING", floor=1, cso=4, row=1, place=6, status=True
    )
    await db_helpers.auth_as(client, admin)

    update_response = await client.patch(
        f"/api/v1/slots/edit/{slot.id}",
        json={"type": "DRYING", "floor": 2, "place": 7, "status": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] is False

    toggle_response = await client.patch(f"/api/v1/slots/{slot.id}/toggle-status")
    assert toggle_response.status_code == 200

    delete_response = await client.delete(f"/api/v1/slots/{slot.id}")
    assert delete_response.status_code == 204

    deleted = await db_session.get(SlotORM, slot.id)
    assert deleted is None

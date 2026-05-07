from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


@pytest.mark.anyio
async def test_admin_crud_role_flow(client, db_helpers) -> None:
    admin = await db_helpers.create_user(telegram_id=9701, username="admin", is_admin=True)
    target = await db_helpers.create_user(
        telegram_id=9702, username="target", is_admin=False, is_banned=False
    )
    await db_helpers.auth_as(client, admin)

    ban_response = await client.patch(f"/api/v1/admin/ban/{target.id}")
    assert ban_response.status_code == 200
    assert ban_response.json()["is_banned"] is True

    edit_response = await client.patch(
        f"/api/v1/admin/edit/{target.id}", json={"username": "patched-user", "is_banned": True}
    )
    assert edit_response.status_code == 200
    assert edit_response.json()["username"] == "patched-user"

    unban_response = await client.patch(f"/api/v1/admin/unban/{target.id}")
    assert unban_response.status_code == 200
    assert unban_response.json()["is_banned"] is False

    history_response = await client.get("/api/v1/admin/history", params={"limit": 20, "offset": 0})
    assert history_response.status_code == 200

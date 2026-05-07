from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_admin_can_ban_unban_edit_toggle_role_and_read_history(client, db_helpers) -> None:
    admin = await db_helpers.create_user(telegram_id=9301, username="admin", is_admin=True)
    target = await db_helpers.create_user(
        telegram_id=4444, username="target", is_admin=False, is_banned=False
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

    history_response = await client.get(
        "/api/v1/admin/history", params={"target_user_id": str(target.id), "limit": 20, "offset": 0}
    )
    assert history_response.status_code == 200

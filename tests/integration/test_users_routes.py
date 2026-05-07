from __future__ import annotations

import pytest

from src.core.db.models.admin_history import AdminAction

pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_admin_can_list_users_with_filters_and_pagination(client, db_helpers) -> None:
    admin = await db_helpers.create_user(telegram_id=9201, username="admin", is_admin=True)
    await db_helpers.create_user(telegram_id=3001, username="alice", is_admin=True, is_banned=False)
    await db_helpers.create_user(telegram_id=3002, username="bob", is_admin=False, is_banned=True)
    await db_helpers.auth_as(client, admin)

    response = await client.get(
        "/api/v1/users/",
        params={
            "name": "ali",
            "is_banned": "false",
            "is_admin": "true",
            "sort_by": "created_at",
            "sort_order": "desc",
            "page": 1,
            "per_page": 10,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["username"] == "alice"


@pytest.mark.anyio
async def test_admin_can_create_and_delete_user(client, db_helpers) -> None:
    admin = await db_helpers.create_user(telegram_id=9202, username="admin", is_admin=True)
    await db_helpers.auth_as(client, admin)

    create_response = await client.post(
        "/api/v1/users/",
        json={
            "id": "98de7a90-3e83-4b10-9513-7efc5d1ad0cc",
            "telegram_id": 3333,
            "username": "new-user",
            "is_banned": False,
            "is_admin": False,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        },
    )
    assert create_response.status_code == 201

    user_id = create_response.json()["id"]
    delete_response = await client.delete(f"/api/v1/users/{user_id}")
    assert delete_response.status_code == 204


@pytest.mark.anyio
async def test_banned_user_can_read_own_ban_info(client, db_helpers) -> None:
    moderator = await db_helpers.create_user(telegram_id=9203, username="mod", is_admin=True)
    user = await db_helpers.create_user(telegram_id=3334, username="banned-user", is_banned=True)

    await db_helpers.create_admin_history_row(
        moderator_id=moderator.id,
        target_user_id=user.id,
        action=AdminAction.BAN,
        description="Violation of rules",
    )
    await db_helpers.auth_as(client, user)

    response = await client.get("/api/v1/users/ban")
    assert response.status_code == 200
    body = response.json()
    assert body["is_banned"] is True
    assert body["description"] == "Violation of rules"

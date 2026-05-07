from __future__ import annotations

import pytest
from sqlalchemy import select

from src.core.db.models import AuthSession, Users

pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_login_sets_auth_cookies_and_persists_user(
    client, db_session, telegram_init_data
) -> None:
    response = await client.post(
        "/api/v1/auth/login", json={"initData": telegram_init_data(777001, "root-admin")}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"

    cookies = "\n".join(response.headers.get_list("set-cookie"))
    assert "access_token=" in cookies
    assert "refresh_token=" in cookies

    user = await db_session.scalar(select(Users).where(Users.telegram_id == 777001))
    assert user is not None
    assert user.username == "root-admin"

    session_row = await db_session.scalar(select(AuthSession).where(AuthSession.user_id == user.id))
    assert session_row is not None
    assert session_row.revoked_at is None


@pytest.mark.anyio
async def test_me_returns_current_user_after_login(client, telegram_init_data) -> None:
    login_response = await client.post(
        "/api/v1/auth/login", json={"initData": telegram_init_data(123456, "alice")}
    )
    assert login_response.status_code == 200

    me_response = await client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    body = me_response.json()
    assert body["telegram_id"] == 123456
    assert body["username"] == "alice"

from __future__ import annotations

import pytest
from sqlalchemy import select

from src.core.db.models import AuthSession, Users

pytestmark = pytest.mark.e2e


@pytest.mark.anyio
async def test_auth_login_refresh_logout_flow(client, db_session, telegram_init_data) -> None:
    login_response = await client.post(
        "/api/v1/auth/login", json={"initData": telegram_init_data(777001, "root-admin")}
    )
    assert login_response.status_code == 200

    me_response = await client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["telegram_id"] == 777001

    user = await db_session.scalar(select(Users).where(Users.telegram_id == 777001))
    old_sessions = list(
        (
            await db_session.execute(select(AuthSession).where(AuthSession.user_id == user.id))
        ).scalars()
    )
    assert len(old_sessions) == 1
    assert old_sessions[0].revoked_at is None

    refresh_response = await client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200

    refreshed_sessions = list(
        (
            await db_session.execute(select(AuthSession).where(AuthSession.user_id == user.id))
        ).scalars()
    )
    assert len(refreshed_sessions) == 2

    logout_response = await client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.json() == {"ok": True}

    me_after_logout = await client.get("/api/v1/auth/me")
    assert me_after_logout.status_code == 401

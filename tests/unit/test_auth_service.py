from __future__ import annotations

import hashlib
import hmac
import json
import urllib.parse
import uuid
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from src.apps.auth.services.auth import AuthService


class FakeUoW:
    def __init__(self) -> None:
        self.session = SimpleNamespace(flush=self._flush)
        self.flushed = False
        self.committed = 0
        self.rolled_back = 0

    async def _flush(self) -> None:
        self.flushed = True

    class _Tx:
        def __init__(self, outer: FakeUoW) -> None:
            self.outer = outer

        async def __aenter__(self):
            return self.outer

        async def __aexit__(self, exc_type, exc, tb) -> None:
            if exc_type is None:
                self.outer.committed += 1
            else:
                self.outer.rolled_back += 1
            return False

    def transaction(self):
        return self._Tx(self)


class FakeUserRepo:
    def __init__(self, user=None) -> None:
        self.user = user or SimpleNamespace(
            id=uuid.uuid4(), telegram_id=12345, username="tester", is_admin=False
        )

    async def upsert_by_telegram(self, payload):
        self.user.telegram_id = payload.telegram_id
        self.user.username = payload.username
        return self.user


class FakeAuthSessionRepo:
    def __init__(self, session=None) -> None:
        self.session = session
        self.created = []
        self.revoked = []

    async def create(self, **kwargs):
        self.created.append(kwargs)
        return kwargs

    async def get_by_jti(self, jti):
        return self.session

    async def revoke(self, jti):
        self.revoked.append(jti)

    async def revoke_all_by_user(self, user_id):
        self.revoked.append(("all", user_id))


class FakeJWTIssuer:
    @staticmethod
    def create_access_token(subject: str, extra_claims=None) -> str:
        return f"access:{subject}:{extra_claims or {}}"

    @staticmethod
    def create_refresh_token(subject: str, jti=None, extra_claims=None):
        return f"refresh:{subject}:{jti}", datetime.now(UTC) + timedelta(days=7)


def build_init_data(bot_token: str, user_payload: dict) -> str:
    data = {
        "auth_date": "1710000000",
        "query_id": "AAEAAAE",
        "user": json.dumps(user_payload, separators=(",", ":")),
    }
    pairs = [f"{k}={v}" for k, v in sorted(data.items())]
    data_check_string = "\n".join(pairs)
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    signature = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    data["hash"] = signature
    return urllib.parse.urlencode(data)


@pytest.mark.anyio
async def test_verify_init_data_extracts_user() -> None:
    service = AuthService(
        FakeUserRepo(), FakeAuthSessionRepo(), "bot-token", FakeJWTIssuer, FakeUoW()
    )
    init_data = build_init_data("bot-token", {"id": 777, "username": "alice"})

    tg_user = service._verify_init_data_and_extract_user(init_data)

    assert tg_user.telegram_id == 777
    assert tg_user.username == "alice"


@pytest.mark.anyio
async def test_verify_init_data_rejects_invalid_signature() -> None:
    service = AuthService(
        FakeUserRepo(), FakeAuthSessionRepo(), "bot-token", FakeJWTIssuer, FakeUoW()
    )
    good = build_init_data("bot-token", {"id": 777, "username": "alice"})
    bad = good.replace("hash=", "hash=broken", 1)

    with pytest.raises(ValueError, match="Invalid initData signature"):
        service._verify_init_data_and_extract_user(bad)


@pytest.mark.anyio
async def test_refresh_tokens_rotates_refresh_session() -> None:
    user_id = uuid.uuid4()
    old_jti = uuid.uuid4()
    existing = SimpleNamespace(
        user_id=user_id, revoked_at=None, expires_at=datetime.now(UTC) + timedelta(hours=1)
    )
    auth_repo = FakeAuthSessionRepo(session=existing)
    service = AuthService(FakeUserRepo(), auth_repo, "bot-token", FakeJWTIssuer, FakeUoW())

    access_token, refresh_token = await service.refresh_tokens(
        {"sub": str(user_id), "jti": str(old_jti), "tg": 999},
        user_agent="pytest",
        ip_address="127.0.0.1",
    )

    assert access_token.startswith(f"access:{user_id}")
    assert refresh_token.startswith(f"refresh:{user_id}:")
    assert auth_repo.revoked == [old_jti]
    assert len(auth_repo.created) == 1
    assert auth_repo.created[0]["user_id"] == user_id
    assert auth_repo.created[0]["user_agent"] == "pytest"


@pytest.mark.anyio
async def test_refresh_tokens_rejects_expired_session() -> None:
    user_id = uuid.uuid4()
    old_jti = uuid.uuid4()
    existing = SimpleNamespace(
        user_id=user_id, revoked_at=None, expires_at=datetime.now(UTC) - timedelta(seconds=1)
    )
    auth_repo = FakeAuthSessionRepo(session=existing)
    service = AuthService(FakeUserRepo(), auth_repo, "bot-token", FakeJWTIssuer, FakeUoW())

    with pytest.raises(HTTPException, match="Refresh token expired"):
        await service.refresh_tokens({"sub": str(user_id), "jti": str(old_jti)})

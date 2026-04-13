import hashlib
import hmac
import json
import urllib.parse
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import Depends, HTTPException, status

from src.apps.auth.repositories.interfaces import IAuthSessionRepo, IUserRepo
from src.apps.auth.schemas.dataclasses.auth import TgUserPayload
from src.core.db.uow import UoW
from src.core.dependencies.admin import is_root_admin_tg
from src.core.security.jwt import get_access_payload, get_jti_from_payload, get_user_id_from_payload


class AuthService:
    def __init__(
        self,
        user_repo: IUserRepo,
        auth_session_repo: IAuthSessionRepo,
        bot_token: str,
        jwt_issuer,
        uow: UoW,
    ):
        self.user_repo = user_repo
        self.auth_session_repo = auth_session_repo
        self.bot_token = bot_token
        self.jwt_issuer = jwt_issuer
        self.uow = uow

    async def login_with_telegram(
        self, init_data_raw: str, user_agent: str | None = None, ip_address: str | None = None
    ) -> tuple[str, str, dict]:
        tg_user = self._verify_init_data_and_extract_user(init_data_raw)

        async with self.uow.transaction():
            user = await self.user_repo.upsert_by_telegram(tg_user)

            if is_root_admin_tg(tg_user.telegram_id) and not user.is_admin:
                user.is_admin = True
                await self.uow.session.flush()

            access_token = self.jwt_issuer.create_access_token(
                subject=str(user.id), extra_claims={"tg": user.telegram_id}
            )

            refresh_jti = uuid.uuid4()
            refresh_token, refresh_expires_at = self.jwt_issuer.create_refresh_token(
                subject=str(user.id), jti=refresh_jti, extra_claims={"tg": user.telegram_id}
            )

            await self.auth_session_repo.create(
                user_id=user.id,
                jti=refresh_jti,
                expires_at=refresh_expires_at,
                user_agent=user_agent,
                ip_address=ip_address,
            )

        public_user = {
            "id": str(user.id),
            "telegram_id": user.telegram_id,
            "username": user.username,
        }
        return access_token, refresh_token, public_user

    async def refresh_tokens(
        self,
        refresh_payload: dict[str, Any],
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str]:
        user_id = get_user_id_from_payload(refresh_payload)
        old_jti = get_jti_from_payload(refresh_payload)
        telegram_id = refresh_payload.get("tg")

        async with self.uow.transaction():
            session = await self.auth_session_repo.get_by_jti(old_jti)

            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session not found"
                )

            if session.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session user mismatch"
                )

            if session.revoked_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked"
                )

            if session.expires_at <= datetime.now(UTC):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
                )

            await self.auth_session_repo.revoke(old_jti)

            new_jti = uuid.uuid4()

            access_token = self.jwt_issuer.create_access_token(
                subject=str(user_id),
                extra_claims={"tg": telegram_id} if telegram_id is not None else None,
            )
            refresh_token, refresh_expires_at = self.jwt_issuer.create_refresh_token(
                subject=str(user_id),
                jti=new_jti,
                extra_claims={"tg": telegram_id} if telegram_id is not None else None,
            )

            await self.auth_session_repo.create(
                user_id=user_id,
                jti=new_jti,
                expires_at=refresh_expires_at,
                user_agent=user_agent,
                ip_address=ip_address,
            )

        return access_token, refresh_token

    async def logout(self, refresh_payload: dict[str, Any]) -> None:
        jti = get_jti_from_payload(refresh_payload)

        async with self.uow.transaction():
            await self.auth_session_repo.revoke(jti)

    async def logout_all(self, user_id: uuid.UUID) -> None:
        async with self.uow.transaction():
            await self.auth_session_repo.revoke_all_by_user(user_id)

    def _verify_init_data_and_extract_user(self, init_data: str) -> TgUserPayload:
        parsed = urllib.parse.parse_qsl(init_data, keep_blank_values=True)
        data = dict(parsed)

        received_hash = data.pop("hash", None)
        if not received_hash:
            raise ValueError("Missing hash in initData")

        pairs = [f"{k}={v}" for k, v in sorted(data.items())]
        data_check_string = "\n".join(pairs)

        secret_key = hmac.new(
            b"WebAppData", self.bot_token.encode("utf-8"), hashlib.sha256
        ).digest()

        computed_hash = hmac.new(
            secret_key, data_check_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        if computed_hash != received_hash:
            raise ValueError("Invalid initData signature")

        user_raw = data.get("user")
        if not user_raw:
            raise ValueError("Missing 'user' in initData")

        user_json = json.loads(user_raw)
        return TgUserPayload(telegram_id=int(user_json["id"]), username=user_json.get("username"))

    @staticmethod
    async def get_current_user_id(
        payload: dict[str, Any] = Depends(get_access_payload),
    ) -> uuid.UUID:
        return get_user_id_from_payload(payload)

    @staticmethod
    async def get_current_telegram_id(
        payload: dict[str, Any] = Depends(get_access_payload),
    ) -> int | None:
        return payload.get("tg")

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyCookie, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

from src.core.config.config import settings

bearer_scheme = HTTPBearer(auto_error=False)
access_cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)
refresh_cookie_scheme = APIKeyCookie(name="refresh_token", auto_error=False)

SECRET_KEY = settings.jwt.secret_key
ALGORITHM = settings.jwt.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt.expires
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(
    subject: str | int,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    subject: str | int,
    jti: uuid.UUID | None = None,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> tuple[str, datetime]:
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    refresh_jti = jti or uuid.uuid4()

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "jti": str(refresh_jti),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    if extra_claims:
        to_encode.update(extra_claims)

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def validate_token_type(payload: dict[str, Any], expected_type: str) -> None:
    token_type = payload.get("type")
    if token_type != expected_type:
        raise ValueError(f"invalid token type: expected {expected_type}, got {token_type}")


def get_user_id_from_payload(payload: dict[str, Any]) -> uuid.UUID:
    sub = payload.get("sub")
    if sub is None:
        raise ValueError("missing 'sub' in token")

    try:
        return uuid.UUID(sub)
    except ValueError as e:
        raise ValueError("invalid 'sub' type") from e


def get_jti_from_payload(payload: dict[str, Any]) -> uuid.UUID:
    jti = payload.get("jti")
    if jti is None:
        raise ValueError("missing 'jti' in token")

    try:
        return uuid.UUID(jti)
    except ValueError as e:
        raise ValueError("invalid 'jti' type") from e


async def get_access_payload(token: str | None = Depends(access_cookie_scheme)) -> dict:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_token(token)
    validate_token_type(payload, "access")
    return payload


async def get_refresh_payload(token: str | None = Depends(refresh_cookie_scheme)) -> dict:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    payload = decode_token(token)
    validate_token_type(payload, "refresh")
    return payload


class JWTIssuer:
    @staticmethod
    def create_access_token(subject: str | int, extra_claims: dict[str, Any] | None = None) -> str:
        return create_access_token(subject=subject, extra_claims=extra_claims)

    @staticmethod
    def create_refresh_token(
        subject: str | int, jti: uuid.UUID | None = None, extra_claims: dict[str, Any] | None = None
    ) -> tuple[str, datetime]:
        return create_refresh_token(subject=subject, jti=jti, extra_claims=extra_claims)

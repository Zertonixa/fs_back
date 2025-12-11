from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Users
from src.core.dependencies.db import get_async_session
from src.core.security.jwt import get_current_payload, get_user_id_from_payload


async def get_current_user(
    payload: dict[str, Any] = Depends(get_current_payload),
    session: AsyncSession = Depends(get_async_session),
) -> Users:
    user_id: UUID = get_user_id_from_payload(payload)

    user = await Users.get_by_id(session, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if getattr(user, "is_banned", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is banned",
        )

    return user


async def get_current_user_id(
    user: Users = Depends(get_current_user),
) -> UUID:
    return user.id


async def get_current_telegram_id(
    payload: dict[str, Any] = Depends(get_current_payload),
) -> int | None:
    return payload.get("tg")

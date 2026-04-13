from fastapi import Depends, HTTPException, status

from src.core.config.config import settings
from src.core.db.models import Users
from src.core.dependencies.user import get_current_user


def is_root_admin_tg(telegram_id: int | None) -> bool:
    return telegram_id is not None and telegram_id in set(settings.security.root_admin_telegram_ids)


def get_is_admin(current_user: Users = Depends(get_current_user)) -> bool:
    return bool(getattr(current_user, "is_admin", False))


async def require_admin(user: Users = Depends(get_current_user)) -> Users:
    if not (
        getattr(user, "is_admin", False) or is_root_admin_tg(getattr(user, "telegram_id", None))
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

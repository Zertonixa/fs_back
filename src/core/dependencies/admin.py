from fastapi import Depends, HTTPException, status

from src.core.db.models import Users
from src.core.security.jwt import get_user_id_from_payload


async def require_admin(user: Users = Depends(get_user_id_from_payload)) -> Users:
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

from fastapi import Depends, HTTPException, status

from src.core.db.models import Users
from src.core.dependencies.user import get_current_user


async def require_admin(user: Users = Depends(get_current_user)) -> Users:
    if not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user

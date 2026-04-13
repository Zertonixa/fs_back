from fastapi import Depends

from src.apps.auth.repositories.sql.auth import UserRepo
from src.apps.auth.repositories.sql.session import AuthSessionRepo
from src.apps.auth.services.auth import AuthService
from src.core.config.config import settings
from src.core.db.uow import UoW
from src.core.dependencies.db import get_uow
from src.core.security.jwt import JWTIssuer


def get_auth_service(uow: UoW = Depends(get_uow)) -> AuthService:
    user_repo = UserRepo(uow.session)
    auth_session_repo = AuthSessionRepo(uow.session)
    return AuthService(
        user_repo=user_repo,
        auth_session_repo=auth_session_repo,
        bot_token=settings.bot.bot_token,
        jwt_issuer=JWTIssuer,
        uow=uow,
    )

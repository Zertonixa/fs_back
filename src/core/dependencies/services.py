from fastapi import Depends

from src.apps.auth.repositories import IUserRepo
from src.apps.auth.services import AuthService
from src.core.config.config import settings
from src.core.db.uow import UnitOfWork
from src.core.dependencies.db import get_uow
from src.core.security import create_access_token


def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    repo = IUserRepo(uow.session)
    return AuthService(user_repo=repo, bot_token=settings.BOT_TOKEN, jwt_issuer=create_access_token)

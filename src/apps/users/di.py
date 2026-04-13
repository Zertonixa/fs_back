from fastapi import Depends

from src.apps.admin_history.repositories.sql.admin_history import AdminHistoryRepo
from src.apps.users.repositories.sql.users import UserRepo
from src.apps.users.services.users import UserService
from src.core.db.uow import UoW
from src.core.dependencies.db import get_uow


def get_users_service(uow: UoW = Depends(get_uow)) -> UserService:
    user_repo = UserRepo(uow.session)
    admin_history = AdminHistoryRepo(uow.session)
    return UserService(repo=user_repo, admin_history_repo=admin_history, uow=uow)

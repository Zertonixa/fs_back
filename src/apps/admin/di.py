from fastapi import Depends

from src.apps.admin_history.repositories.sql.admin_history import AdminHistoryRepo
from src.core.db.uow import UoW
from src.core.dependencies.db import get_uow

from .repositories.sql import AdminUserRepo
from .services import AdminService


def get_admin_service(uow: UoW = Depends(get_uow)) -> AdminService:
    repo = AdminUserRepo(uow.session)
    admin_history = AdminHistoryRepo(uow.session)
    return AdminService(repo=repo, history_repo=admin_history, uow=uow)

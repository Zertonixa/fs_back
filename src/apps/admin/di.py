from fastapi import Depends

from src.core.db.uow import UoW
from src.core.dependencies.db import get_uow

from .repositories.sql import AdminUserRepo
from .services import AdminService


def get_admin_service(uow: UoW = Depends(get_uow)) -> AdminService:
    repo = AdminUserRepo(uow.session)
    return AdminService(repo=repo, uow=uow)

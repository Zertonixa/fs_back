from fastapi import Depends

from src.apps.slots.repositories.sql.slots import SlotRepo
from src.apps.slots.services.slots import SlotService
from src.core.db.uow import UoW
from src.core.dependencies.db import get_uow


def get_slot_service(uow: UoW = Depends(get_uow)) -> SlotService:
    slot_repo = SlotRepo(uow.session)
    return SlotService(slot_repo=slot_repo, uow=uow)

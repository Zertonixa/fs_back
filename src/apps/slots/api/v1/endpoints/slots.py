from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status as http_status

from src.core.db.models.slot import Type as SlotType
from src.core.dependencies.user import get_current_user_id

from ....di import get_slot_service
from ....schemas.pydantic.slots import Slot, SlotCreate, SlotUpdate
from ....services.slots import SlotService

router = APIRouter(prefix="/slots", dependencies=[Depends(get_current_user_id)])


@router.get("/", status_code=http_status.HTTP_200_OK)
async def get_all_slots(
    type_: SlotType | None = Query(
        None, alias="type", description="Тип устройства (WASHING, DRYING)"
    ),
    floor_: int = Query(1),
    cso_: int = Query(4),
    slot_service: SlotService = Depends(get_slot_service),
):
    slots = await slot_service.get_matrix(type_, floor_, cso_)
    return slots


@router.post("/", status_code=http_status.HTTP_201_CREATED)
async def create_slot(
    slot_data: SlotCreate, slot_service: SlotService = Depends(get_slot_service)
) -> Slot:
    created = await slot_service.create(slot_data)
    return Slot(
        id=created.id,
        type=created.type,
        floor=created.floor,
        place=created.place,
        status=created.status,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.delete("/{slot_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_slot(slot_id: UUID, slot_service: SlotService = Depends(get_slot_service)) -> None:
    await slot_service.delete(slot_id)


@router.patch("/edit/{slot_id}", status_code=http_status.HTTP_200_OK)
async def edit_slot(
    slot_id: UUID, slot_data: SlotUpdate, slot_service: SlotService = Depends(get_slot_service)
) -> Slot:
    updated = await slot_service.update(slot_id, slot_data.to_dc())
    return Slot(
        id=updated.id,
        type=updated.type,
        floor=updated.floor,
        place=updated.place,
        status=updated.status,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )

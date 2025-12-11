from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.mappers.slots import dc_to_orm, orm_to_dc
from src.core.db.models.slot import Slot as SlotORM
from src.core.db.models.slot import Type as SlotType

from ...schemas.dataclasses.slots import Slot as SlotDC
from ..interfaces import ISlotRepo


class SlotRepo(ISlotRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        type_: SlotType | None = None,
        floor_: int | None = None,
        cso_: int | None = None,
    ) -> list[SlotDC]:

        stmt = select(SlotORM).order_by(SlotORM.row, SlotORM.place)

        if type_:
            stmt = stmt.where(SlotORM.type == type_)

        if floor_ is not None:
            stmt = stmt.where(SlotORM.floor == floor_)

        if cso_ is not None:
            stmt = stmt.where(SlotORM.cso == cso_)

        rows = await self.session.scalars(stmt)
        slots_orm = list(rows)

        return [orm_to_dc(s) for s in slots_orm]

    async def get_by_id(self, slot_id: UUID) -> SlotDC | None:
        obj = await SlotORM.get_by_id(self.session, slot_id)
        if not obj:
            return None
        return orm_to_dc(obj)

    async def create(self, slot: SlotDC) -> SlotDC:
        orm_obj = dc_to_orm(slot)
        self.session.add(orm_obj)
        await self.session.flush()
        return orm_to_dc(orm_obj)

    async def update(self, slot_id: UUID, slot: SlotDC) -> SlotDC | None:
        obj = await self.session.get(SlotORM, slot_id)
        if not obj:
            return None

        obj.type = slot.type
        obj.floor = slot.floor
        obj.place = slot.place
        obj.status = slot.status

        await self.session.flush()
        return orm_to_dc(obj)

    async def delete(self, slot_id: UUID) -> None:
        obj = await self.session.get(SlotORM, slot_id)
        if not obj:
            return
        await self.session.delete(obj)
        await self.session.flush()

    async def get_by_params(
        self,
        type_: SlotType,
        floor_: int,
        cso_: int,
        row_: int,
        place_: int,
    ) -> SlotDC | None:
        stmt = (
            select(SlotORM)
            .where(
                SlotORM.type == type_,
                SlotORM.floor == floor_,
                SlotORM.cso == cso_,
                SlotORM.row == row_,
                SlotORM.place == place_,
            )
            .limit(1)
        )
        obj = await self.session.scalar(stmt)
        if obj is None:
            return None
        return orm_to_dc(obj)

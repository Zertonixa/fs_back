from src.apps.slots.schemas.dataclasses.slots import Slot as SlotDC
from src.core.db.models.slot import Slot as SlotORM


def orm_to_dc(orm: SlotORM) -> SlotDC:
    return SlotDC(
        id=orm.id,
        type=orm.type,
        floor=orm.floor,
        place=orm.place,
        row=orm.row,
        cso=orm.cso,
        status=orm.status,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
    )


def dc_to_orm(dc: SlotDC) -> SlotORM:
    return SlotORM(
        type=dc.type, floor=dc.floor, place=dc.place, cso=dc.cso, row=dc.row, status=dc.status
    )

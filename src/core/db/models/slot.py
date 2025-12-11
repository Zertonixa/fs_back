import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, func
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

if TYPE_CHECKING:
    from .booking import Booking
    from .booking_slot import BookingSlots


class Type(enum.StrEnum):
    WASHING = "WASHING"
    DRYING = "DRYING"


class Slot(Base):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[Type] = mapped_column(
        PgEnum(Type, name="slot_type", create_type=True),
        nullable=False,
    )
    floor: Mapped[int] = mapped_column(Integer)
    cso: Mapped[int] = mapped_column(Integer)
    row: Mapped[int] = mapped_column(Integer)
    place: Mapped[int] = mapped_column(Integer)
    status: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    booking_slots: Mapped[list["BookingSlots"]] = relationship(
        back_populates="slot",
        cascade="all, delete-orphan",
    )

    bookings: Mapped[list["Booking"]] = relationship(
        secondary="bookingslots",
        back_populates="slots",
        lazy="selectin",
    )

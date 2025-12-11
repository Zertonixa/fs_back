from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db.base import Base

if TYPE_CHECKING:
    from .booking import Booking
    from .slot import Slot


class BookingSlots(Base):

    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey("booking.id", ondelete="CASCADE"),
        primary_key=True,
    )
    slot_id: Mapped[UUID] = mapped_column(
        ForeignKey("slot.id", ondelete="CASCADE"),
        primary_key=True,
    )

    booking: Mapped["Booking"] = relationship(
        back_populates="booking_slots",
    )
    slot: Mapped["Slot"] = relationship(
        back_populates="booking_slots",
    )

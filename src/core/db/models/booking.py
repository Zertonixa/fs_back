import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .booking_slot import BookingSlots
    from .slot import Slot

from src.core.db import Base


class BookingStatus(enum.StrEnum):
    NEW = "NEW"
    CANCELLED = "CANCELLED"
    DONE = "DONE"


class BookingType(enum.StrEnum):
    WASHING = "WASHING"
    DRYING = "DRYING"


class Booking(Base):

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    start_reminder_task_id: Mapped[str | None] = mapped_column(nullable=True)

    end_reminder_task_id: Mapped[str | None] = mapped_column(nullable=True)

    complete_task_id: Mapped[str | None] = mapped_column(nullable=True)

    status: Mapped[BookingStatus] = mapped_column(
        PgEnum(BookingStatus, name="booking_status", create_type=True),
        default=BookingStatus.NEW,
        nullable=False,
    )

    type: Mapped[BookingType] = mapped_column(
        PgEnum(BookingType, name="booking_type", create_type=True),
        nullable=False,
    )

    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    booking_slots: Mapped[list["BookingSlots"]] = relationship(
        back_populates="booking",
        cascade="all, delete-orphan",
    )

    slots: Mapped[list["Slot"]] = relationship(
        secondary="bookingslots",
        back_populates="bookings",
        lazy="selectin",
    )

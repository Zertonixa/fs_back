import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column

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

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    machine_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("machines.id", ondelete="SET NULL"), index=True, nullable=True
    )

    status: Mapped[BookingStatus] = mapped_column(
        PgEnum(BookingStatus, name="booking_status", create_type=True),
        default=BookingStatus.NEW,
        nullable=False,
    )

    type: Mapped[BookingType] = mapped_column(
        PgEnum(BookingType, name="booking_type", create_type=True), nullable=False
    )

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db.base import Base
from src.core.enums.complaints import ComplaintStatus

if TYPE_CHECKING:
    from src.core.db.models.complaints_files import ComplaintFile


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(
            ComplaintStatus,
            name="complaint_status",
            values_callable=lambda enum_cls: [item.name for item in enum_cls],
        ),
        default=ComplaintStatus.SENT,
        server_default=ComplaintStatus.SENT.name,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    files: Mapped[list[ComplaintFile]] = relationship(
        back_populates="complaint", cascade="all, delete-orphan"
    )

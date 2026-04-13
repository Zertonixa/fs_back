import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class AdminAction(StrEnum):
    BAN = "ban"
    UNBAN = "unban"
    GRANT_ADMIN = "grant_admin"
    REVOKE_ADMIN = "revoke_admin"
    CHANGE_SLOT = "change_slot"


if TYPE_CHECKING:
    from .slot import Slot
    from .users import Users


class AdminHistory(Base):
    __tablename__ = "admin_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    moderator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    target_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    slot_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("slot.id", ondelete="SET NULL"), nullable=True, index=True
    )

    action: Mapped[AdminAction] = mapped_column(
        SAEnum(AdminAction, name="admin_action"), nullable=False, index=True
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)

    moderator: Mapped["Users"] = relationship(
        "Users", foreign_keys=[moderator_id], back_populates="admin_history"
    )

    target_user: Mapped["Users | None"] = relationship(
        "Users", foreign_keys=[target_user_id], back_populates="admin_history_as_target"
    )

    slot: Mapped["Slot | None"] = relationship(
        "Slot", foreign_keys=[slot_id], back_populates="admin_history"
    )

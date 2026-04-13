import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base

if TYPE_CHECKING:
    from src.core.db.models.admin_history import AdminHistory
    from src.core.db.models.auth import AuthSession


class Users(Base):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    admin_history: Mapped[list["AdminHistory"]] = relationship(
        "AdminHistory",
        back_populates="moderator",
        foreign_keys="AdminHistory.moderator_id",
        cascade="all, delete-orphan",
    )

    admin_history_as_target: Mapped[list["AdminHistory"]] = relationship(
        "AdminHistory", back_populates="target_user", foreign_keys="AdminHistory.target_user_id"
    )

    auth_sessions: Mapped[list["AuthSession"]] = relationship(
        "AuthSession", back_populates="user", cascade="all, delete-orphan"
    )

"""Platform user persistence (auth IAM — not a planning/runtime domain entity)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base


class PlatformUser(Base):
    __tablename__ = "platform_users"
    __table_args__ = (
        Index("idx_platform_users_username", "username", unique=True),
        Index("idx_platform_users_role", "role"),
    )

    username: Mapped[str] = mapped_column(String(150), primary_key=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(512), nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

"""WBSItem ORM model (Planning Layer)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.activity_instance import ActivityInstance
    from backend.phase1.models.project import Project


class WBSItem(Base):
    __tablename__ = "wbs_items"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "code",
            name="wbs_items_project_id_code_key",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')",
            name="wbs_items_status_check",
        ),
        Index("idx_wbs_items_project_id", "project_id"),
        Index("idx_wbs_items_parent_id", "parent_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "projects.id",
            name="wbs_items_project_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    parent_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "wbs_items.id",
            name="wbs_items_parent_id_fkey",
            ondelete="SET NULL",
        ),
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="ACTIVE",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    project: Mapped[Project] = relationship(back_populates="wbs_items")
    parent: Mapped[WBSItem | None] = relationship(
        remote_side=[id],
        back_populates="children",
    )
    children: Mapped[list[WBSItem]] = relationship(
        back_populates="parent",
    )
    activity_instances: Mapped[list[ActivityInstance]] = relationship(
        back_populates="wbs_item",
    )

"""ActivityInstance ORM model (Construction Reality Layer)."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.location import Location
    from backend.phase1.models.project import Project
    from backend.phase1.models.wbs_item import WBSItem


class ActivityInstance(Base):
    __tablename__ = "activity_instances"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "code",
            name="activity_instances_project_id_code_key",
        ),
        UniqueConstraint(
            "project_id",
            "wbs_item_id",
            "location_id",
            name="activity_instances_project_wbs_location_key",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')",
            name="activity_instances_status_check",
        ),
        Index("idx_activity_instances_project_id", "project_id"),
        Index("idx_activity_instances_wbs_item_id", "wbs_item_id"),
        Index("idx_activity_instances_location_id", "location_id"),
        Index("idx_activity_instances_status", "status"),
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
            name="activity_instances_project_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    wbs_item_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "wbs_items.id",
            name="activity_instances_wbs_item_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    location_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "locations.id",
            name="activity_instances_location_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_finish: Mapped[date | None] = mapped_column(Date)
    planned_duration_days: Mapped[int | None] = mapped_column(Integer)
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

    project: Mapped[Project] = relationship(back_populates="activity_instances")
    wbs_item: Mapped[WBSItem] = relationship(back_populates="activity_instances")
    location: Mapped[Location] = relationship(back_populates="activity_instances")

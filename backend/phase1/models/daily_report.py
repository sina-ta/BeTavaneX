"""DailyReport ORM model (Execution Evidence Layer)."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.phase1.models.work_order import WorkOrder


class DailyReport(Base):
    __tablename__ = "daily_reports"
    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'SUBMITTED', 'REVIEWED', 'ACCEPTED', 'REJECTED')",
            name="daily_reports_status_check",
        ),
        Index("idx_daily_reports_work_order_id", "work_order_id"),
        Index("idx_daily_reports_report_date", "report_date"),
        Index("idx_daily_reports_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    work_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "work_orders.id",
            name="daily_reports_work_order_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="DRAFT",
    )
    summary: Mapped[str | None] = mapped_column(Text)
    execution_notes: Mapped[str | None] = mapped_column(Text)
    issue_notes: Mapped[str | None] = mapped_column(Text)
    delay_notes: Mapped[str | None] = mapped_column(Text)
    weather_notes: Mapped[str | None] = mapped_column(Text)
    evidence_metadata: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSONB)
    submitted_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reported_manpower: Mapped[int | None] = mapped_column(
        Integer,
        server_default=text("0"),
    )
    reported_equipment: Mapped[int | None] = mapped_column(
        Integer,
        server_default=text("0"),
    )
    reported_material_entries: Mapped[int | None] = mapped_column(
        Integer,
        server_default=text("0"),
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

    work_order: Mapped[WorkOrder] = relationship(back_populates="daily_reports")

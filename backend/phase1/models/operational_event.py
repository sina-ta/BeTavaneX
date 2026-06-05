"""OperationalEvent ORM model (Operational Lineage Layer).

Append-only, immutable operational event ledger. This coexists with the
state-oriented domain tables; it does not replace them and is never the source of
truth for current state. Rows are written once and never updated or deleted.

See ``docs/cosc/event-ledger-foundation.md`` for semantics.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from backend.phase1.events.taxonomy import SUPPORTED_EVENT_TYPES

_EVENT_TYPE_CHECK = "event_type IN (" + ", ".join(
    f"'{event_type}'" for event_type in sorted(SUPPORTED_EVENT_TYPES)
) + ")"


class OperationalEvent(Base):
    __tablename__ = "operational_events"
    __table_args__ = (
        CheckConstraint(_EVENT_TYPE_CHECK, name="operational_events_event_type_check"),
        Index(
            "idx_operational_events_aggregate",
            "aggregate_type",
            "aggregate_id",
        ),
        Index("idx_operational_events_event_type", "event_type"),
        Index("idx_operational_events_occurred_at", "occurred_at"),
        Index("idx_operational_events_actor", "actor"),
        Index("idx_operational_events_causality_reference", "causality_reference"),
    )

    event_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    actor: Mapped[str] = mapped_column(String(150), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    # Optional soft link to a prior event_id establishing lineage. Intentionally
    # NOT a foreign key: the ledger must stay append-only and decoupled.
    causality_reference: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    # `metadata` is reserved by SQLAlchemy's declarative base, so the Python
    # attribute is `event_metadata` while the DB column is `metadata`.
    event_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)
    # Server-stamped ledger write time (when the row was appended), distinct from
    # `occurred_at` (when the operation happened, set by the recorder).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

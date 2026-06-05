"""OperationalDependencyEdge ORM model (Runtime Hardening P1).

Explicit, authoritative dependency edges between operational entities. Coexists
with FK/junction structural dependencies; does not replace them. Semantics are
stamped at creation from ``edge_taxonomy``; P1 does not execute propagation.

See ``docs/architecture/runtime-hardening-p1-report.md``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from backend.phase1.dependency_edges.taxonomy import (
    EDGE_STATUS_ACTIVE,
    SUPPORTED_AUTHORITY_LEVELS,
    SUPPORTED_BLOCKING_SEMANTICS,
    SUPPORTED_DEPENDENCY_TYPES,
    SUPPORTED_EDGE_STATUSES,
    SUPPORTED_ENTITY_TYPES,
    SUPPORTED_PROPAGATION_SEMANTICS,
)

_ENTITY_TYPE_CHECK = "source_entity_type IN (" + ", ".join(
    f"'{value}'" for value in sorted(SUPPORTED_ENTITY_TYPES)
) + ") AND target_entity_type IN (" + ", ".join(
    f"'{value}'" for value in sorted(SUPPORTED_ENTITY_TYPES)
) + ")"

_DEPENDENCY_TYPE_CHECK = "dependency_type IN (" + ", ".join(
    f"'{value}'" for value in sorted(SUPPORTED_DEPENDENCY_TYPES)
) + ")"

_AUTHORITY_CHECK = "authority_level IN (" + ", ".join(
    f"'{value}'" for value in sorted(SUPPORTED_AUTHORITY_LEVELS)
) + ")"

_BLOCKING_CHECK = "blocking_semantics IN (" + ", ".join(
    f"'{value}'" for value in sorted(SUPPORTED_BLOCKING_SEMANTICS)
) + ")"

_PROPAGATION_CHECK = "propagation_semantics IN (" + ", ".join(
    f"'{value}'" for value in sorted(SUPPORTED_PROPAGATION_SEMANTICS)
) + ")"

_STATUS_CHECK = "lifecycle_status IN (" + ", ".join(
    f"'{value}'" for value in sorted(SUPPORTED_EDGE_STATUSES)
) + ")"


class OperationalDependencyEdge(Base):
    __tablename__ = "operational_dependency_edges"
    __table_args__ = (
        CheckConstraint(_ENTITY_TYPE_CHECK, name="ode_entity_type_check"),
        CheckConstraint(_DEPENDENCY_TYPE_CHECK, name="ode_dependency_type_check"),
        CheckConstraint(_AUTHORITY_CHECK, name="ode_authority_level_check"),
        CheckConstraint(_BLOCKING_CHECK, name="ode_blocking_semantics_check"),
        CheckConstraint(_PROPAGATION_CHECK, name="ode_propagation_semantics_check"),
        CheckConstraint(_STATUS_CHECK, name="ode_lifecycle_status_check"),
        CheckConstraint(
            "source_entity_id != target_entity_id",
            name="ode_no_self_link_check",
        ),
        Index("idx_ode_project_id", "project_id"),
        Index("idx_ode_dependency_type", "dependency_type"),
        Index("idx_ode_lifecycle_status", "lifecycle_status"),
        Index(
            "idx_ode_source",
            "source_entity_type",
            "source_entity_id",
        ),
        Index(
            "idx_ode_target",
            "target_entity_type",
            "target_entity_id",
        ),
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
            name="ode_project_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    source_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(80), nullable=False)
    authority_level: Mapped[str] = mapped_column(String(30), nullable=False)
    blocking_semantics: Mapped[str] = mapped_column(String(50), nullable=False)
    propagation_semantics: Mapped[str] = mapped_column(String(50), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=EDGE_STATUS_ACTIVE,
    )
    created_by: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deactivated_by: Mapped[str | None] = mapped_column(String(150))
    deactivation_reason: Mapped[str | None] = mapped_column(Text)
    edge_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

"""Repository for explicit operational dependency edges."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.dependency_edges.taxonomy import EDGE_STATUS_ACTIVE
from backend.phase1.models.operational_dependency_edge import OperationalDependencyEdge
from backend.phase1.repositories.base_repository import BaseRepository


class OperationalDependencyEdgeRepository(BaseRepository[OperationalDependencyEdge]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, OperationalDependencyEdge)

    def list_for_project(
        self,
        project_id: UUID,
        *,
        dependency_type: str | None = None,
        lifecycle_status: str | None = EDGE_STATUS_ACTIVE,
        offset: int = 0,
        limit: int = 200,
    ) -> list[OperationalDependencyEdge]:
        statement = select(OperationalDependencyEdge).where(
            OperationalDependencyEdge.project_id == project_id,
        )
        if dependency_type is not None:
            statement = statement.where(
                OperationalDependencyEdge.dependency_type == dependency_type,
            )
        if lifecycle_status is not None:
            statement = statement.where(
                OperationalDependencyEdge.lifecycle_status == lifecycle_status,
            )
        statement = (
            statement.order_by(OperationalDependencyEdge.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())

    def find_active_identity(
        self,
        *,
        project_id: UUID,
        source_entity_type: str,
        source_entity_id: UUID,
        target_entity_type: str,
        target_entity_id: UUID,
        dependency_type: str,
    ) -> OperationalDependencyEdge | None:
        statement = (
            select(OperationalDependencyEdge)
            .where(OperationalDependencyEdge.project_id == project_id)
            .where(
                OperationalDependencyEdge.source_entity_type == source_entity_type,
            )
            .where(OperationalDependencyEdge.source_entity_id == source_entity_id)
            .where(
                OperationalDependencyEdge.target_entity_type == target_entity_type,
            )
            .where(OperationalDependencyEdge.target_entity_id == target_entity_id)
            .where(OperationalDependencyEdge.dependency_type == dependency_type)
            .where(OperationalDependencyEdge.lifecycle_status == EDGE_STATUS_ACTIVE)
        )
        return self._session.scalars(statement).first()

    def find_active_reverse(
        self,
        *,
        project_id: UUID,
        source_entity_type: str,
        source_entity_id: UUID,
        target_entity_type: str,
        target_entity_id: UUID,
        dependency_type: str,
    ) -> OperationalDependencyEdge | None:
        return self.find_active_identity(
            project_id=project_id,
            source_entity_type=target_entity_type,
            source_entity_id=target_entity_id,
            target_entity_type=source_entity_type,
            target_entity_id=source_entity_id,
            dependency_type=dependency_type,
        )

    def trace_entity(
        self,
        project_id: UUID,
        *,
        entity_type: str,
        entity_id: UUID,
        lifecycle_status: str | None = EDGE_STATUS_ACTIVE,
    ) -> tuple[list[OperationalDependencyEdge], list[OperationalDependencyEdge]]:
        """Return (outgoing, incoming) edges for an entity within a project."""
        outgoing_stmt = select(OperationalDependencyEdge).where(
            OperationalDependencyEdge.project_id == project_id,
            OperationalDependencyEdge.source_entity_type == entity_type,
            OperationalDependencyEdge.source_entity_id == entity_id,
        )
        incoming_stmt = select(OperationalDependencyEdge).where(
            OperationalDependencyEdge.project_id == project_id,
            OperationalDependencyEdge.target_entity_type == entity_type,
            OperationalDependencyEdge.target_entity_id == entity_id,
        )
        if lifecycle_status is not None:
            outgoing_stmt = outgoing_stmt.where(
                OperationalDependencyEdge.lifecycle_status == lifecycle_status,
            )
            incoming_stmt = incoming_stmt.where(
                OperationalDependencyEdge.lifecycle_status == lifecycle_status,
            )
        outgoing = list(
            self._session.scalars(
                outgoing_stmt.order_by(OperationalDependencyEdge.created_at.asc()),
            ).all(),
        )
        incoming = list(
            self._session.scalars(
                incoming_stmt.order_by(OperationalDependencyEdge.created_at.asc()),
            ).all(),
        )
        return outgoing, incoming

"""Integrity rules for explicit operational dependency edges (P1).

Validates edge creation/deactivation without executing propagation or graph
traversal. Grounded in ``dependency-semantics-stabilization.md`` and
``runtime-authority-boundaries.md``.
"""

from __future__ import annotations

from uuid import UUID

from backend.phase1.dependency_edges.taxonomy import (
    EDGE_STATUS_ACTIVE,
    is_sequencing_dependency_type,
    semantics_for,
)
from backend.phase1.models.operational_dependency_edge import OperationalDependencyEdge


class DependencyEdgeIntegrityError(ValueError):
    """Raised when an edge violates authoritative integrity rules."""


def validate_entity_pair_for_dependency_type(
    *,
    dependency_type: str,
    source_entity_type: str,
    target_entity_type: str,
) -> None:
    semantics = semantics_for(dependency_type)
    if source_entity_type not in semantics.allowed_source_types:
        raise DependencyEdgeIntegrityError(
            f"dependency type {dependency_type!r} does not allow "
            f"source entity type {source_entity_type!r}",
        )
    if target_entity_type not in semantics.allowed_target_types:
        raise DependencyEdgeIntegrityError(
            f"dependency type {dependency_type!r} does not allow "
            f"target entity type {target_entity_type!r}",
        )


def validate_same_project(
    *,
    project_id: UUID,
    source_project_id: UUID,
    target_project_id: UUID,
) -> None:
    if source_project_id != project_id or target_project_id != project_id:
        raise DependencyEdgeIntegrityError(
            "source and target entities must belong to the edge project_id",
        )
    if source_project_id != target_project_id:
        raise DependencyEdgeIntegrityError(
            "cross-project dependency edges are forbidden",
        )


def validate_no_self_link(
    *,
    source_entity_type: str,
    source_entity_id: UUID,
    target_entity_type: str,
    target_entity_id: UUID,
) -> None:
    if (
        source_entity_type == target_entity_type
        and source_entity_id == target_entity_id
    ):
        raise DependencyEdgeIntegrityError(
            "self-referential dependency edges are forbidden",
        )


def validate_no_direct_reverse_active_edge(
    *,
    dependency_type: str,
    reverse_exists: bool,
) -> None:
    if not is_sequencing_dependency_type(dependency_type):
        return
    if reverse_exists:
        raise DependencyEdgeIntegrityError(
            f"direct reverse active edge exists for sequencing type "
            f"{dependency_type!r}",
        )


def validate_no_duplicate_active_edge(existing: OperationalDependencyEdge | None) -> None:
    if existing is not None and existing.lifecycle_status == EDGE_STATUS_ACTIVE:
        raise DependencyEdgeIntegrityError(
            "an active dependency edge with the same identity already exists",
        )


def validate_edge_active(edge: OperationalDependencyEdge) -> None:
    if edge.lifecycle_status != EDGE_STATUS_ACTIVE:
        raise DependencyEdgeIntegrityError(
            f"dependency edge {edge.id} is not active",
        )

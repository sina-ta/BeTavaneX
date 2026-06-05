"""Pydantic schemas for operational dependency edges (P1)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DependencyEdgeCreate(BaseModel):
    source_entity_type: str
    source_entity_id: UUID
    target_entity_type: str
    target_entity_id: UUID
    dependency_type: str
    metadata: dict[str, Any] | None = None


class DependencyEdgeDeactivate(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)


class DependencyEdgeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    source_entity_type: str
    source_entity_id: UUID
    target_entity_type: str
    target_entity_id: UUID
    dependency_type: str
    authority_level: str
    blocking_semantics: str
    propagation_semantics: str
    lifecycle_status: str
    created_by: str
    created_at: datetime
    deactivated_at: datetime | None = None
    deactivated_by: str | None = None
    deactivation_reason: str | None = None
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias="edge_metadata",
    )


class DependencyEdgeTraceRead(BaseModel):
    entity_type: str
    entity_id: UUID
    outgoing: list[DependencyEdgeRead]
    incoming: list[DependencyEdgeRead]


class OperationalEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: UUID
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    actor: str
    occurred_at: datetime
    causality_reference: UUID | None = None
    payload: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias="event_metadata",
    )
    created_at: datetime


class DependencyEdgeLineageRead(BaseModel):
    edge_id: UUID
    events: list[OperationalEventRead]

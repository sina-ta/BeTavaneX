"""Lightweight optimistic concurrency using ``updated_at`` tokens (no version column)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TypeVar
from uuid import UUID

from backend.phase1.exceptions import ConcurrencyConflictError

ModelT = TypeVar("ModelT")


def _normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def timestamps_match(stored: datetime, expected: datetime) -> bool:
    return _normalize_timestamp(stored) == _normalize_timestamp(expected)


def assert_unchanged(
    *,
    resource_type: str,
    resource_id: UUID,
    stored_updated_at: datetime | None,
    expected_updated_at: datetime | None,
) -> None:
    if expected_updated_at is None:
        return
    if stored_updated_at is None:
        raise ConcurrencyConflictError(resource_type, str(resource_id))
    if not timestamps_match(stored_updated_at, expected_updated_at):
        raise ConcurrencyConflictError(resource_type, str(resource_id))


def touch_updated_at(entity: object) -> None:
    if hasattr(entity, "updated_at"):
        entity.updated_at = datetime.now(timezone.utc)  # type: ignore[attr-defined]

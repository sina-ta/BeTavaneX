"""Shared CRUD helpers for Phase 1 repositories."""

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.exceptions import ConcurrencyConflictError
from backend.phase1.repositories.optimistic import (
    assert_unchanged,
    touch_updated_at,
)

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Persistence-only data access; callers own transaction commit/rollback."""

    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    def get_by_id(self, entity_id: UUID) -> ModelT | None:
        return self._session.get(self._model, entity_id)

    def list(
        self,
        *,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[ModelT]:
        statement = select(self._model).offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

    def create(self, entity: ModelT) -> ModelT:
        self._session.add(entity)
        self._session.flush()
        self._session.refresh(entity)
        return entity

    def update(
        self,
        entity: ModelT,
        *,
        expected_updated_at: datetime | None = None,
        resource_type: str | None = None,
    ) -> ModelT:
        if expected_updated_at is not None and hasattr(entity, "id"):
            persisted = self.get_by_id(entity.id)  # type: ignore[attr-defined]
            if persisted is None:
                raise ConcurrencyConflictError(
                    resource_type or self._model.__name__,
                    str(entity.id),  # type: ignore[attr-defined]
                )
            assert_unchanged(
                resource_type=resource_type or self._model.__name__,
                resource_id=entity.id,  # type: ignore[attr-defined]
                stored_updated_at=getattr(persisted, "updated_at", None),
                expected_updated_at=expected_updated_at,
            )
        touch_updated_at(entity)
        self._session.add(entity)
        self._session.flush()
        self._session.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        from backend.phase1.integrity.delete_policy import assert_delete_allowed

        assert_delete_allowed(self._model)
        self._session.delete(entity)
        self._session.flush()

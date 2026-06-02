"""Shared CRUD helpers for Phase 1 repositories."""

from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

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

    def update(self, entity: ModelT) -> ModelT:
        self._session.add(entity)
        self._session.flush()
        self._session.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        self._session.delete(entity)
        self._session.flush()

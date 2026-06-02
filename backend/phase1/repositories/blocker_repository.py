"""Blocker persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.blocker import Blocker
from backend.phase1.repositories.base_repository import BaseRepository


class BlockerRepository(BaseRepository[Blocker]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Blocker)

    def list(
        self,
        *,
        workflow_step_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[Blocker]:
        statement = select(Blocker)
        if workflow_step_id is not None:
            statement = statement.where(Blocker.workflow_step_id == workflow_step_id)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

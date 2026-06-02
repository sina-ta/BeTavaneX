"""Approval persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.approval import Approval
from backend.phase1.repositories.base_repository import BaseRepository


class ApprovalRepository(BaseRepository[Approval]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Approval)

    def list(
        self,
        *,
        workflow_step_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[Approval]:
        statement = select(Approval)
        if workflow_step_id is not None:
            statement = statement.where(Approval.workflow_step_id == workflow_step_id)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

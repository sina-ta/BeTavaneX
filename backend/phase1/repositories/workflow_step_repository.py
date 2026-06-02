"""WorkflowStep persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.workflow_step import WorkflowStep
from backend.phase1.repositories.base_repository import BaseRepository


class WorkflowStepRepository(BaseRepository[WorkflowStep]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, WorkflowStep)

    def list(
        self,
        *,
        activity_instance_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[WorkflowStep]:
        statement = select(WorkflowStep)
        if activity_instance_id is not None:
            statement = statement.where(
                WorkflowStep.activity_instance_id == activity_instance_id,
            )
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

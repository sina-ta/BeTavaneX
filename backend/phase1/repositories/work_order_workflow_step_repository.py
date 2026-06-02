"""WorkOrderWorkflowStep junction persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.work_order_workflow_step import WorkOrderWorkflowStep
from backend.phase1.repositories.base_repository import BaseRepository


class WorkOrderWorkflowStepRepository(BaseRepository[WorkOrderWorkflowStep]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, WorkOrderWorkflowStep)

    def list(
        self,
        *,
        work_order_id: UUID | None = None,
        workflow_step_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[WorkOrderWorkflowStep]:
        statement = select(WorkOrderWorkflowStep)
        if work_order_id is not None:
            statement = statement.where(
                WorkOrderWorkflowStep.work_order_id == work_order_id,
            )
        if workflow_step_id is not None:
            statement = statement.where(
                WorkOrderWorkflowStep.workflow_step_id == workflow_step_id,
            )
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

    def get_by_work_order_and_step(
        self,
        work_order_id: UUID,
        workflow_step_id: UUID,
    ) -> WorkOrderWorkflowStep | None:
        statement = select(WorkOrderWorkflowStep).where(
            WorkOrderWorkflowStep.work_order_id == work_order_id,
            WorkOrderWorkflowStep.workflow_step_id == workflow_step_id,
        )
        return self._session.scalar(statement)

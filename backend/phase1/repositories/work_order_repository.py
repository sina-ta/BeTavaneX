"""WorkOrder persistence repository."""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.models.work_order import WorkOrder
from backend.phase1.models.work_order_workflow_step import WorkOrderWorkflowStep
from backend.phase1.repositories.base_repository import BaseRepository

WorkOrderSortField = Literal["planned_date", "created_at"]
SortDirection = Literal["asc", "desc"]


class WorkOrderRepository(BaseRepository[WorkOrder]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, WorkOrder)

    def _filtered_statement(
        self,
        *,
        project_id: UUID,
        status: str | None = None,
        workflow_step_id: UUID | None = None,
        planned_date_from: date | None = None,
        planned_date_to: date | None = None,
    ):
        statement = select(WorkOrder).where(WorkOrder.project_id == project_id)
        if status:
            statement = statement.where(WorkOrder.status == status)
        if planned_date_from is not None:
            statement = statement.where(WorkOrder.planned_date >= planned_date_from)
        if planned_date_to is not None:
            statement = statement.where(WorkOrder.planned_date <= planned_date_to)
        if workflow_step_id is not None:
            statement = statement.join(
                WorkOrderWorkflowStep,
                WorkOrderWorkflowStep.work_order_id == WorkOrder.id,
            ).where(WorkOrderWorkflowStep.workflow_step_id == workflow_step_id)
        return statement

    def count_filtered(
        self,
        *,
        project_id: UUID,
        status: str | None = None,
        workflow_step_id: UUID | None = None,
        planned_date_from: date | None = None,
        planned_date_to: date | None = None,
    ) -> int:
        base = self._filtered_statement(
            project_id=project_id,
            status=status,
            workflow_step_id=workflow_step_id,
            planned_date_from=planned_date_from,
            planned_date_to=planned_date_to,
        )
        statement = select(func.count()).select_from(base.subquery())
        return int(self._session.scalar(statement) or 0)

    def list_filtered(
        self,
        *,
        project_id: UUID,
        status: str | None = None,
        workflow_step_id: UUID | None = None,
        planned_date_from: date | None = None,
        planned_date_to: date | None = None,
        sort_by: WorkOrderSortField = "planned_date",
        sort_dir: SortDirection = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> list[WorkOrder]:
        statement = self._filtered_statement(
            project_id=project_id,
            status=status,
            workflow_step_id=workflow_step_id,
            planned_date_from=planned_date_from,
            planned_date_to=planned_date_to,
        )
        sort_column = (
            WorkOrder.planned_date if sort_by == "planned_date" else WorkOrder.created_at
        )
        statement = statement.order_by(
            sort_column.asc() if sort_dir == "asc" else sort_column.desc(),
        )
        statement = statement.offset(offset).limit(limit)
        return list(self._session.scalars(statement).unique().all())

    def list(
        self,
        *,
        project_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[WorkOrder]:
        if project_id is None:
            return super().list(offset=offset, limit=limit)
        return self.list_filtered(
            project_id=project_id,
            offset=offset,
            limit=limit if limit is not None else 10_000,
        )

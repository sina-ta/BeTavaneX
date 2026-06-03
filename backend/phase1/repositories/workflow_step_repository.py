"""WorkflowStep persistence repository."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.models.workflow_step import WorkflowStep
from backend.phase1.repositories.base_repository import BaseRepository

WorkflowStepSortField = Literal["planned_start", "progress_percent", "created_at"]
SortDirection = Literal["asc", "desc"]


class WorkflowStepRepository(BaseRepository[WorkflowStep]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, WorkflowStep)

    def _filtered_statement(
        self,
        *,
        activity_instance_id: UUID,
        status: str | None = None,
        ready: bool | None = None,
    ):
        statement = select(WorkflowStep).where(
            WorkflowStep.activity_instance_id == activity_instance_id,
        )
        if status:
            statement = statement.where(WorkflowStep.status == status)
        if ready is not None:
            statement = statement.where(WorkflowStep.ready == ready)
        return statement

    def count_filtered(
        self,
        *,
        activity_instance_id: UUID,
        status: str | None = None,
        ready: bool | None = None,
    ) -> int:
        base = self._filtered_statement(
            activity_instance_id=activity_instance_id,
            status=status,
            ready=ready,
        )
        statement = select(func.count()).select_from(base.subquery())
        return int(self._session.scalar(statement) or 0)

    def list(
        self,
        *,
        activity_instance_id: UUID | None = None,
        status: str | None = None,
        ready: bool | None = None,
        sort_by: WorkflowStepSortField = "created_at",
        sort_dir: SortDirection = "desc",
        offset: int = 0,
        limit: int | None = None,
    ) -> list[WorkflowStep]:
        if activity_instance_id is None:
            return super().list(offset=offset, limit=limit)

        statement = self._filtered_statement(
            activity_instance_id=activity_instance_id,
            status=status,
            ready=ready,
        )
        sort_column = {
            "planned_start": WorkflowStep.planned_start,
            "progress_percent": WorkflowStep.progress_percent,
            "created_at": WorkflowStep.created_at,
        }[sort_by]
        statement = statement.order_by(
            sort_column.asc() if sort_dir == "asc" else sort_column.desc(),
        )
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

    def count_by_project_id(
        self,
        project_id: UUID,
        *,
        status: str | None = None,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(WorkflowStep)
            .join(
                ActivityInstance,
                WorkflowStep.activity_instance_id == ActivityInstance.id,
            )
            .where(ActivityInstance.project_id == project_id)
        )
        if status:
            statement = statement.where(WorkflowStep.status == status)
        return int(self._session.scalar(statement) or 0)

    def list_by_project_id(
        self,
        project_id: UUID,
        *,
        status: str | None = None,
        sort_by: WorkflowStepSortField = "created_at",
        sort_dir: SortDirection = "desc",
        offset: int = 0,
        limit: int = 500,
    ) -> list[WorkflowStep]:
        statement = (
            select(WorkflowStep)
            .join(
                ActivityInstance,
                WorkflowStep.activity_instance_id == ActivityInstance.id,
            )
            .where(ActivityInstance.project_id == project_id)
        )
        if status:
            statement = statement.where(WorkflowStep.status == status)
        sort_column = {
            "planned_start": WorkflowStep.planned_start,
            "progress_percent": WorkflowStep.progress_percent,
            "created_at": WorkflowStep.created_at,
        }[sort_by]
        statement = statement.order_by(
            sort_column.asc() if sort_dir == "asc" else sort_column.desc(),
        )
        statement = statement.offset(offset).limit(limit)
        return list(self._session.scalars(statement).all())

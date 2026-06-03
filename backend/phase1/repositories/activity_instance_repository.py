"""ActivityInstance persistence repository."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.repositories.base_repository import BaseRepository

ActivityInstanceSortField = Literal["planned_start", "created_at"]
SortDirection = Literal["asc", "desc"]


class ActivityInstanceRepository(BaseRepository[ActivityInstance]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ActivityInstance)

    def get_by_code(self, project_id: UUID, code: str) -> ActivityInstance | None:
        statement = select(ActivityInstance).where(
            ActivityInstance.project_id == project_id,
            ActivityInstance.code == code,
        )
        return self._session.scalar(statement)

    def _filtered_statement(
        self,
        *,
        project_id: UUID,
        wbs_item_id: UUID | None = None,
        location_id: UUID | None = None,
        status: str | None = None,
    ):
        statement = select(ActivityInstance).where(
            ActivityInstance.project_id == project_id,
        )
        if wbs_item_id is not None:
            statement = statement.where(ActivityInstance.wbs_item_id == wbs_item_id)
        if location_id is not None:
            statement = statement.where(ActivityInstance.location_id == location_id)
        if status:
            statement = statement.where(ActivityInstance.status == status)
        return statement

    def count_filtered(
        self,
        *,
        project_id: UUID,
        wbs_item_id: UUID | None = None,
        location_id: UUID | None = None,
        status: str | None = None,
    ) -> int:
        base = self._filtered_statement(
            project_id=project_id,
            wbs_item_id=wbs_item_id,
            location_id=location_id,
            status=status,
        )
        statement = select(func.count()).select_from(base.subquery())
        return int(self._session.scalar(statement) or 0)

    def list_filtered(
        self,
        *,
        project_id: UUID,
        wbs_item_id: UUID | None = None,
        location_id: UUID | None = None,
        status: str | None = None,
        sort_by: ActivityInstanceSortField = "created_at",
        sort_dir: SortDirection = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> list[ActivityInstance]:
        statement = self._filtered_statement(
            project_id=project_id,
            wbs_item_id=wbs_item_id,
            location_id=location_id,
            status=status,
        )
        sort_column = (
            ActivityInstance.planned_start
            if sort_by == "planned_start"
            else ActivityInstance.created_at
        )
        statement = statement.order_by(
            sort_column.asc() if sort_dir == "asc" else sort_column.desc(),
        )
        statement = statement.offset(offset).limit(limit)
        return list(self._session.scalars(statement).all())

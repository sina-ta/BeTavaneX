"""Project persistence repository."""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.phase1.models.project import Project
from backend.phase1.repositories.base_repository import BaseRepository

ProjectSortField = Literal["planned_start", "created_at"]
SortDirection = Literal["asc", "desc"]


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Project)

    def get_by_code(self, code: str) -> Project | None:
        statement = select(Project).where(Project.code == code)
        return self._session.scalar(statement)

    def _filtered_statement(
        self,
        *,
        project_ids: set[UUID] | None = None,
        name: str | None = None,
        status: str | None = None,
        planned_start_from: date | None = None,
        planned_start_to: date | None = None,
        planned_finish_from: date | None = None,
        planned_finish_to: date | None = None,
    ):
        statement = select(Project)
        if project_ids is not None:
            if not project_ids:
                statement = statement.where(Project.id.is_(None))
            else:
                statement = statement.where(Project.id.in_(project_ids))
        if name:
            pattern = f"%{name}%"
            statement = statement.where(
                or_(Project.name.ilike(pattern), Project.code.ilike(pattern)),
            )
        if status:
            statement = statement.where(Project.status == status)
        if planned_start_from is not None:
            statement = statement.where(Project.planned_start >= planned_start_from)
        if planned_start_to is not None:
            statement = statement.where(Project.planned_start <= planned_start_to)
        if planned_finish_from is not None:
            statement = statement.where(Project.planned_finish >= planned_finish_from)
        if planned_finish_to is not None:
            statement = statement.where(Project.planned_finish <= planned_finish_to)
        return statement

    def count_filtered(
        self,
        *,
        project_ids: set[UUID] | None = None,
        name: str | None = None,
        status: str | None = None,
        planned_start_from: date | None = None,
        planned_start_to: date | None = None,
        planned_finish_from: date | None = None,
        planned_finish_to: date | None = None,
    ) -> int:
        base = self._filtered_statement(
            project_ids=project_ids,
            name=name,
            status=status,
            planned_start_from=planned_start_from,
            planned_start_to=planned_start_to,
            planned_finish_from=planned_finish_from,
            planned_finish_to=planned_finish_to,
        )
        statement = select(func.count()).select_from(base.subquery())
        return int(self._session.scalar(statement) or 0)

    def list_filtered(
        self,
        *,
        project_ids: set[UUID] | None = None,
        name: str | None = None,
        status: str | None = None,
        planned_start_from: date | None = None,
        planned_start_to: date | None = None,
        planned_finish_from: date | None = None,
        planned_finish_to: date | None = None,
        sort_by: ProjectSortField = "created_at",
        sort_dir: SortDirection = "desc",
        offset: int = 0,
        limit: int = 50,
    ) -> list[Project]:
        statement = self._filtered_statement(
            project_ids=project_ids,
            name=name,
            status=status,
            planned_start_from=planned_start_from,
            planned_start_to=planned_start_to,
            planned_finish_from=planned_finish_from,
            planned_finish_to=planned_finish_to,
        )
        sort_column = (
            Project.planned_start if sort_by == "planned_start" else Project.created_at
        )
        statement = statement.order_by(
            sort_column.asc() if sort_dir == "asc" else sort_column.desc(),
        )
        statement = statement.offset(offset).limit(limit)
        return list(self._session.scalars(statement).all())

"""DailyReport persistence repository."""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.models.daily_report import DailyReport
from backend.phase1.repositories.base_repository import BaseRepository

DailyReportSortField = Literal["report_date", "created_at"]
SortDirection = Literal["asc", "desc"]


class DailyReportRepository(BaseRepository[DailyReport]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DailyReport)

    def _filtered_statement(
        self,
        *,
        work_order_id: UUID,
        status: str | None = None,
        report_date_from: date | None = None,
        report_date_to: date | None = None,
    ):
        statement = select(DailyReport).where(DailyReport.work_order_id == work_order_id)
        if status:
            statement = statement.where(DailyReport.status == status)
        if report_date_from is not None:
            statement = statement.where(DailyReport.report_date >= report_date_from)
        if report_date_to is not None:
            statement = statement.where(DailyReport.report_date <= report_date_to)
        return statement

    def count_filtered(
        self,
        *,
        work_order_id: UUID,
        status: str | None = None,
        report_date_from: date | None = None,
        report_date_to: date | None = None,
    ) -> int:
        base = self._filtered_statement(
            work_order_id=work_order_id,
            status=status,
            report_date_from=report_date_from,
            report_date_to=report_date_to,
        )
        statement = select(func.count()).select_from(base.subquery())
        return int(self._session.scalar(statement) or 0)

    def list(
        self,
        *,
        work_order_id: UUID | None = None,
        status: str | None = None,
        report_date_from: date | None = None,
        report_date_to: date | None = None,
        sort_by: DailyReportSortField = "report_date",
        sort_dir: SortDirection = "desc",
        offset: int = 0,
        limit: int | None = None,
    ) -> list[DailyReport]:
        if work_order_id is None:
            return super().list(offset=offset, limit=limit)

        statement = self._filtered_statement(
            work_order_id=work_order_id,
            status=status,
            report_date_from=report_date_from,
            report_date_to=report_date_to,
        )
        sort_column = (
            DailyReport.report_date if sort_by == "report_date" else DailyReport.created_at
        )
        statement = statement.order_by(
            sort_column.asc() if sort_dir == "asc" else sort_column.desc(),
        )
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

"""DailyReport persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.daily_report import DailyReport
from backend.phase1.repositories.base_repository import BaseRepository


class DailyReportRepository(BaseRepository[DailyReport]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, DailyReport)

    def list(
        self,
        *,
        work_order_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[DailyReport]:
        statement = select(DailyReport)
        if work_order_id is not None:
            statement = statement.where(DailyReport.work_order_id == work_order_id)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

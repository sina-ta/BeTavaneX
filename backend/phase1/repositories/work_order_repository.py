"""WorkOrder persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.work_order import WorkOrder
from backend.phase1.repositories.base_repository import BaseRepository


class WorkOrderRepository(BaseRepository[WorkOrder]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, WorkOrder)

    def list(
        self,
        *,
        project_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[WorkOrder]:
        statement = select(WorkOrder)
        if project_id is not None:
            statement = statement.where(WorkOrder.project_id == project_id)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

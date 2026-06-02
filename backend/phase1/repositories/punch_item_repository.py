"""PunchItem persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.punch_item import PunchItem
from backend.phase1.repositories.base_repository import BaseRepository


class PunchItemRepository(BaseRepository[PunchItem]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, PunchItem)

    def list(
        self,
        *,
        workflow_step_id: UUID | None = None,
        inspection_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[PunchItem]:
        statement = select(PunchItem)
        if workflow_step_id is not None:
            statement = statement.where(
                PunchItem.workflow_step_id == workflow_step_id,
            )
        if inspection_id is not None:
            statement = statement.where(PunchItem.inspection_id == inspection_id)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

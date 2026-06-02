"""BOQMapping persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.boq_mapping import BOQMapping
from backend.phase1.repositories.base_repository import BaseRepository


class BOQMappingRepository(BaseRepository[BOQMapping]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, BOQMapping)

    def list(
        self,
        *,
        workflow_step_id: UUID | None = None,
        boq_item_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[BOQMapping]:
        statement = select(BOQMapping)
        if workflow_step_id is not None:
            statement = statement.where(
                BOQMapping.workflow_step_id == workflow_step_id,
            )
        if boq_item_id is not None:
            statement = statement.where(BOQMapping.boq_item_id == boq_item_id)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

    def get_by_step_and_item(
        self,
        workflow_step_id: UUID,
        boq_item_id: UUID,
    ) -> BOQMapping | None:
        statement = select(BOQMapping).where(
            BOQMapping.workflow_step_id == workflow_step_id,
            BOQMapping.boq_item_id == boq_item_id,
        )
        return self._session.scalar(statement)

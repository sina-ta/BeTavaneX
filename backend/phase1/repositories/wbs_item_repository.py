"""WBSItem persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.wbs_item import WBSItem
from backend.phase1.repositories.base_repository import BaseRepository


class WBSItemRepository(BaseRepository[WBSItem]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, WBSItem)

    def list(
        self,
        *,
        project_id: UUID | None = None,
        parent_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[WBSItem]:
        statement = select(WBSItem)
        if project_id is not None:
            statement = statement.where(WBSItem.project_id == project_id)
        if parent_id is not None:
            statement = statement.where(WBSItem.parent_id == parent_id)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

    def get_by_code(self, project_id: UUID, code: str) -> WBSItem | None:
        statement = select(WBSItem).where(
            WBSItem.project_id == project_id,
            WBSItem.code == code,
        )
        return self._session.scalar(statement)

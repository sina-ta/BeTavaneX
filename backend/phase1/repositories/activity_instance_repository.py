"""ActivityInstance persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.activity_instance import ActivityInstance
from backend.phase1.repositories.base_repository import BaseRepository


class ActivityInstanceRepository(BaseRepository[ActivityInstance]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ActivityInstance)

    def get_by_code(self, project_id: UUID, code: str) -> ActivityInstance | None:
        statement = select(ActivityInstance).where(
            ActivityInstance.project_id == project_id,
            ActivityInstance.code == code,
        )
        return self._session.scalar(statement)

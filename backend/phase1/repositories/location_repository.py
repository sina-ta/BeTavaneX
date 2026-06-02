"""Location persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.location import Location
from backend.phase1.repositories.base_repository import BaseRepository


class LocationRepository(BaseRepository[Location]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Location)

    def list(
        self,
        *,
        project_id: UUID | None = None,
        parent_id: UUID | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[Location]:
        statement = select(Location)
        if project_id is not None:
            statement = statement.where(Location.project_id == project_id)
        if parent_id is not None:
            statement = statement.where(Location.parent_id == parent_id)
        statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

    def get_by_code(self, project_id: UUID, code: str) -> Location | None:
        statement = select(Location).where(
            Location.project_id == project_id,
            Location.code == code,
        )
        return self._session.scalar(statement)

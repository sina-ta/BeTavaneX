"""Project persistence repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.project import Project
from backend.phase1.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Project)

    def get_by_code(self, code: str) -> Project | None:
        statement = select(Project).where(Project.code == code)
        return self._session.scalar(statement)

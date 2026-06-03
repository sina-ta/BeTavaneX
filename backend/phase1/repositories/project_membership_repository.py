"""Project membership persistence repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.phase1.models.project_membership import ProjectMembership
from backend.phase1.repositories.base_repository import BaseRepository


class ProjectMembershipRepository(BaseRepository[ProjectMembership]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ProjectMembership)

    def grant(self, username: str, project_id: UUID) -> None:
        existing = self._session.scalar(
            select(ProjectMembership).where(
                ProjectMembership.username == username,
                ProjectMembership.project_id == project_id,
            ),
        )
        if existing is not None:
            return
        self.create(
            ProjectMembership(username=username, project_id=project_id),
        )

    def list_project_ids_for_username(self, username: str) -> set[UUID]:
        statement = select(ProjectMembership.project_id).where(
            ProjectMembership.username == username,
        )
        return set(self._session.scalars(statement).all())

    def count_for_username(self, username: str) -> int:
        statement = (
            select(func.count())
            .select_from(ProjectMembership)
            .where(ProjectMembership.username == username)
        )
        return int(self._session.scalar(statement) or 0)

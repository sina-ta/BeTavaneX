"""Database-backed project membership for Phase 1 pilot scoping.

Not a domain entity — auth infrastructure only. Admins bypass membership (all projects).
"""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status

from backend.phase1.auth.auth import ROLE_ADMIN, ROLE_INVESTOR, ROLE_SUPERVISOR, ROLE_WORKER, User
from backend.phase1.auth.user_service import UserAuthService
from backend.phase1.repositories.project_membership_repository import (
    ProjectMembershipRepository,
)


class ProjectAccessService:
    def __init__(
        self,
        membership_repository: ProjectMembershipRepository,
        user_auth_service: UserAuthService,
    ) -> None:
        self._membership = membership_repository
        self._user_auth = user_auth_service

    def grant_project_access(self, username: str, project_id: UUID) -> None:
        self._membership.grant(username, project_id)

    def get_accessible_project_ids(self, user: User) -> set[UUID] | None:
        """Return None when the user may access every project (admin)."""
        if user.role == ROLE_ADMIN:
            return None
        return self._membership.list_project_ids_for_username(user.username)

    def user_can_access_project(self, user: User, project_id: UUID) -> bool:
        allowed = self.get_accessible_project_ids(user)
        if allowed is None:
            return True
        return project_id in allowed

    def ensure_project_access(self, user: User, project_id: UUID) -> None:
        if not self.user_can_access_project(user, project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project access denied",
            )

    def register_new_project(self, project_id: UUID, creator: User) -> None:
        self.grant_project_access(creator.username, project_id)
        for username in self._user_auth.list_usernames_by_roles((ROLE_INVESTOR,)):
            self.grant_project_access(username, project_id)

    def grant_project_operational_team(self, project_id: UUID) -> None:
        for username in self._user_auth.list_usernames_by_roles(
            (ROLE_SUPERVISOR, ROLE_WORKER),
        ):
            self.grant_project_access(username, project_id)

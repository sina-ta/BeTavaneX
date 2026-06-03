"""Auth infrastructure dependency providers."""

from __future__ import annotations

from fastapi import Depends

from backend.phase1.auth.project_access import ProjectAccessService
from backend.phase1.auth.user_service import UserAuthService
from backend.phase1.dependencies.auth_users import get_user_auth_service
from backend.phase1.dependencies.repositories import get_project_membership_repository
from backend.phase1.repositories.project_membership_repository import (
    ProjectMembershipRepository,
)


def get_project_access_service(
    membership_repository: ProjectMembershipRepository = Depends(
        get_project_membership_repository,
    ),
    user_auth_service: UserAuthService = Depends(get_user_auth_service),
) -> ProjectAccessService:
    return ProjectAccessService(membership_repository, user_auth_service)

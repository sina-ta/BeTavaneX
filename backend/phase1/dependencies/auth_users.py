"""User auth service dependency."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.phase1.auth.user_service import UserAuthService
from backend.phase1.repositories.platform_user_repository import (
    PlatformUserRepository,
)


def get_platform_user_repository(
    session: Session = Depends(get_db),
) -> PlatformUserRepository:
    return PlatformUserRepository(session)


def get_user_auth_service(
    repository: PlatformUserRepository = Depends(get_platform_user_repository),
) -> UserAuthService:
    return UserAuthService(repository)

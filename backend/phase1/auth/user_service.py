"""Database-backed user authentication service."""

from __future__ import annotations

from backend.phase1.auth.user_models import User, UserInDB
from backend.phase1.auth.security import hash_password, verify_password
from backend.phase1.models.platform_user import PlatformUser
from backend.phase1.repositories.platform_user_repository import (
    PlatformUserRepository,
)


def _to_user_in_db(row: PlatformUser) -> UserInDB:
    return UserInDB(
        username=row.username,
        role=row.role,
        disabled=row.disabled,
        hashed_password=row.hashed_password,
    )


class UserAuthService:
    def __init__(self, repository: PlatformUserRepository) -> None:
        self._repository = repository

    def get_user(self, username: str) -> UserInDB | None:
        row = self._repository.get_by_username(username)
        if row is None:
            return None
        return _to_user_in_db(row)

    def authenticate_user(self, username: str, password: str) -> UserInDB | None:
        user = self.get_user(username)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user

    def list_usernames_by_roles(self, roles: tuple[str, ...]) -> list[str]:
        return self._repository.list_usernames_by_roles(roles)

    def ensure_seed_users(self, seed_users: dict[str, tuple[str, str]]) -> None:
        """Idempotently upsert pilot users (username -> role, plain password)."""
        for username, (role, password) in seed_users.items():
            self._repository.upsert_user(
                username=username,
                role=role,
                hashed_password=hash_password(password),
                disabled=False,
            )

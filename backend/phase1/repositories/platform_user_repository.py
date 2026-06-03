"""Platform user persistence repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.phase1.models.platform_user import PlatformUser
from backend.phase1.repositories.base_repository import BaseRepository


class PlatformUserRepository(BaseRepository[PlatformUser]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, PlatformUser)

    def get_by_username(self, username: str) -> PlatformUser | None:
        return self._session.get(PlatformUser, username)

    def upsert_user(
        self,
        *,
        username: str,
        role: str,
        hashed_password: str,
        disabled: bool = False,
    ) -> PlatformUser:
        existing = self.get_by_username(username)
        if existing is not None:
            existing.role = role
            existing.hashed_password = hashed_password
            existing.disabled = disabled
            self._session.flush()
            return existing

        return self.create(
            PlatformUser(
                username=username,
                role=role,
                hashed_password=hashed_password,
                disabled=disabled,
            ),
        )

    def list_usernames_by_roles(self, roles: tuple[str, ...]) -> list[str]:
        if not roles:
            return []
        statement = select(PlatformUser.username).where(PlatformUser.role.in_(roles))
        return list(self._session.scalars(statement).all())

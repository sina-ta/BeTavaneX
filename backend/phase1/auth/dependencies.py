"""Auth dependencies: current-user resolution and role-based authorization."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable

from fastapi import Depends, HTTPException, status

from backend.phase1.auth.auth import User, oauth2_scheme
from backend.phase1.auth.security import TokenError, decode_token
from backend.phase1.auth.user_service import UserAuthService
from backend.phase1.dependencies.auth_users import get_user_auth_service

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_auth: UserAuthService = Depends(get_user_auth_service),
) -> User:
    try:
        payload = decode_token(token)
    except TokenError as exc:
        raise _CREDENTIALS_EXCEPTION from exc

    username = payload.get("sub")
    token_role = payload.get("role")
    if not isinstance(username, str):
        raise _CREDENTIALS_EXCEPTION

    user = user_auth.get_user(username)
    if user is None:
        raise _CREDENTIALS_EXCEPTION

    if isinstance(token_role, str) and token_role != user.role:
        raise _CREDENTIALS_EXCEPTION

    return User(username=user.username, role=user.role, disabled=user.disabled)


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def require_roles(*roles: str) -> Callable[[User], User]:
    """Dependency factory enforcing that the current user has one of `roles`."""
    allowed: Iterable[str] = set(roles)

    def _dependency(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role for this operation",
            )
        return current_user

    return _dependency

"""Authentication security utilities (architecture skeleton).

Prepared for future JWT, role-based access, and refresh tokens.
Full implementation is intentionally deferred.
"""

from datetime import timedelta
from typing import Any, Optional

# Placeholder configuration — replace via environment in auth phase
SECRET_KEY = "CHANGE_ME_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token (not yet implemented)."""
    _ = (data, expires_delta)
    return ""


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token (not yet implemented)."""
    _ = (data, expires_delta)
    return ""


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT token (not yet implemented)."""
    _ = token
    return {}


def hash_password(password: str) -> str:
    """Hash a plaintext password (not yet implemented)."""
    _ = password
    return ""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (not yet implemented)."""
    _ = (plain_password, hashed_password)
    return False


def get_current_user_roles() -> list[str]:
    """Return roles for the current user (RBAC skeleton)."""
    return []

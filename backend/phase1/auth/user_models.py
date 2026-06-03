"""Auth domain models and pilot seed constants (no service imports)."""

from __future__ import annotations

from pydantic import BaseModel

ROLE_ADMIN = "admin"
ROLE_SUPERVISOR = "supervisor"
ROLE_WORKER = "worker"
ROLE_INVESTOR = "investor"

PILOT_SEED_USERS: dict[str, tuple[str, str]] = {
    "admin": (ROLE_ADMIN, "admin"),
    "supervisor": (ROLE_SUPERVISOR, "supervisor"),
    "worker": (ROLE_WORKER, "worker"),
    "investor": (ROLE_INVESTOR, "investor"),
}


class User(BaseModel):
    username: str
    role: str
    disabled: bool = False


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

#!/usr/bin/env python3
"""Seed persisted platform users for Phase 1 pilot IAM."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_STARTUP_VALIDATION", "true")

from backend.db.session import SessionLocal
from backend.phase1.auth.auth import PILOT_SEED_USERS
from backend.phase1.auth.user_service import UserAuthService
from backend.phase1.repositories.platform_user_repository import PlatformUserRepository


def main() -> None:
    session = SessionLocal()
    try:
        service = UserAuthService(PlatformUserRepository(session))
        service.ensure_seed_users(PILOT_SEED_USERS)
        session.commit()
        print(f"Seeded {len(PILOT_SEED_USERS)} platform users.")
    finally:
        session.close()


if __name__ == "__main__":
    main()

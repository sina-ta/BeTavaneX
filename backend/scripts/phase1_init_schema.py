#!/usr/bin/env python3
"""Create Phase 1 tables on the configured database (manual / CI — not Docker entrypoint).

Docker Compose uses ``alembic upgrade head`` only. See ``backend/docker-entrypoint.sh``.
"""

from __future__ import annotations

import backend.phase1.models  # noqa: F401 — register ORM metadata
from backend.db.base import Base
from backend.db.session import engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Phase 1 schema ensured (create_all).")


if __name__ == "__main__":
    main()

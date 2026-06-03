"""Phase 1 API startup validation (database + optional Alembic head)."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from backend.config import get_settings, validate_environment_settings

logger = logging.getLogger(__name__)


def validate_startup(*, require_alembic_head: bool | None = None) -> None:
    """Fail fast when PostgreSQL is unreachable or migrations are behind."""
    if os.getenv("SKIP_STARTUP_VALIDATION", "").lower() in {"1", "true", "yes"}:
        logger.info("Phase 1 startup validation skipped (SKIP_STARTUP_VALIDATION)")
        return

    validate_environment_settings()
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        msg = f"PostgreSQL unavailable at startup: {exc}"
        raise RuntimeError(msg) from exc

    if require_alembic_head is None:
        require_alembic_head = os.getenv("REQUIRE_ALEMBIC_HEAD", "false").lower() in {
            "1",
            "true",
            "yes",
        }

    if not require_alembic_head:
        logger.info("Phase 1 startup: database connectivity OK")
        return

    try:
        from alembic.config import Config
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory
    except ImportError as exc:
        raise RuntimeError("Alembic required when REQUIRE_ALEMBIC_HEAD=true") from exc

    repo_root = Path(__file__).resolve().parents[2]
    alembic_ini = os.getenv("ALEMBIC_INI", str(repo_root / "backend" / "alembic.ini"))
    alembic_cfg = Config(alembic_ini)
    script = ScriptDirectory.from_config(alembic_cfg)
    head = script.get_current_head()

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current = context.get_current_revision()

    if current != head:
        msg = f"Alembic revision mismatch: db={current} head={head}"
        raise RuntimeError(msg)

    logger.info("Phase 1 startup: database OK, Alembic at head (%s)", head)

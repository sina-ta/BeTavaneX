"""Database engine and session management for Phase 1."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import get_settings
from backend.observability.slow_query import register_slow_query_logging

_settings = get_settings()

engine = create_engine(
    _settings.database_url,
    echo=_settings.db_echo,
    pool_pre_ping=True,
    pool_size=_settings.db_pool_size,
    max_overflow=_settings.db_max_overflow,
    future=True,
)

register_slow_query_logging(
    engine,
    threshold_ms=float(_settings.slow_query_ms),
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped session: commit on success, rollback on error, always close."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

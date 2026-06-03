"""SQLAlchemy slow-query logging (lightweight, no APM stack)."""

from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger("betavanx.slow_query")


def register_slow_query_logging(
    engine: Engine,
    *,
    threshold_ms: float = 500,
) -> None:
    """Log SQL statements that exceed the configured threshold."""

    @event.listens_for(engine, "before_cursor_execute")
    def _before(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        if context is not None:
            context._betavanx_query_start = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def _after(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        if context is None or not hasattr(context, "_betavanx_query_start"):
            return

        elapsed_ms = (time.perf_counter() - context._betavanx_query_start) * 1000
        if elapsed_ms < threshold_ms:
            return

        preview = " ".join(statement.split())
        if len(preview) > 240:
            preview = f"{preview[:240]}..."

        logger.warning(
            "slow_query elapsed_ms=%.1f sql=%s",
            elapsed_ms,
            preview,
            extra={
                "event": "slow_query",
                "duration_ms": elapsed_ms,
            },
        )

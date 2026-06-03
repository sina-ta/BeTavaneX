"""Structured operational audit logging for multi-user pilot (no new domain tables)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from backend.phase1.analytics.audit_store import append_audit_record
from backend.phase1.auth.auth import User

logger = logging.getLogger("betavanx.operational_audit")

MutationCategory = Literal[
    "planning",
    "execution",
    "governance",
    "query",
    "conflict",
]


def log_operational_action(
    user: User,
    action: str,
    *,
    mutation_category: MutationCategory = "execution",
    project_id: UUID | None = None,
    resource_type: str | None = None,
    resource_id: UUID | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    payload = {
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "username": user.username,
        "role": user.role,
        "mutation_category": mutation_category,
        "action": action,
        "project_id": str(project_id) if project_id else None,
        "resource_type": resource_type,
        "resource_id": str(resource_id) if resource_id else None,
        "detail": detail or {},
    }
    logger.info("operational_audit %s", json.dumps(payload, default=str))
    try:
        append_audit_record(payload)
    except OSError:
        logger.warning("operational_audit_jsonl_write_failed", exc_info=True)


def log_concurrency_conflict(
    user: User,
    *,
    action: str,
    resource_type: str,
    resource_id: UUID | str,
    project_id: UUID | None = None,
    detail: dict[str, Any] | None = None,
) -> None:
    merged = dict(detail or {})
    merged["conflict_resource_id"] = str(resource_id)
    log_operational_action(
        user,
        action,
        mutation_category="conflict",
        project_id=project_id,
        resource_type=resource_type,
        detail=merged,
    )

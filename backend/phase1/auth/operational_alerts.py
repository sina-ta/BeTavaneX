"""Operational alerts for duplicate or conflicting runtime actions."""

from __future__ import annotations

import logging
from uuid import UUID

logger = logging.getLogger("betavanx.operational_alerts")


def alert_duplicate_assignment(
    *,
    work_order_id: UUID,
    workflow_step_id: UUID,
    username: str | None = None,
) -> None:
    logger.warning(
        "duplicate_assignment work_order_id=%s workflow_step_id=%s username=%s",
        work_order_id,
        workflow_step_id,
        username,
    )


def alert_duplicate_approval(
    *,
    workflow_step_id: UUID,
    approval_type: str,
    username: str | None = None,
) -> None:
    logger.warning(
        "duplicate_approval workflow_step_id=%s approval_type=%s username=%s",
        workflow_step_id,
        approval_type,
        username,
    )

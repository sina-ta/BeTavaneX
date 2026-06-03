"""Pilot feedback router — lightweight operational capture for controlled pilots."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, status

from backend.phase1.auth.auth import User
from backend.phase1.auth.dependencies import get_current_active_user
from backend.phase1.auth.operational_audit import log_operational_action
from backend.phase1.pilot.feedback_store import append_pilot_feedback
from backend.phase1.schemas.pilot_feedback_schema import PilotFeedbackCreate

router = APIRouter(prefix="/pilot", tags=["pilot"])
logger = logging.getLogger("betavanx.pilot_metrics")


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
def submit_pilot_feedback(
    payload: PilotFeedbackCreate,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    record = append_pilot_feedback(
        username=current_user.username,
        role=current_user.role,
        category=payload.category,
        message=payload.message,
        page_path=payload.page_path,
        project_id=payload.project_id,
    )
    log_operational_action(
        current_user,
        "pilot_feedback",
        mutation_category="execution",
        project_id=payload.project_id,
        detail={
            "category": payload.category,
            "page_path": payload.page_path,
            "message_preview": payload.message[:200],
        },
    )
    logger.info(
        "pilot_metric feedback_submitted category=%s role=%s",
        payload.category,
        current_user.role,
    )
    return {
        "status": "recorded",
        "recorded_at": record["recorded_at"],
    }

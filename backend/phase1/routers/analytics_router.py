"""Lightweight adoption analytics (Stage 27 — JSONL + optional DB snapshot)."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.phase1.analytics.adoption_service import build_adoption_summary
from backend.phase1.analytics.executive_visibility_service import (
    build_executive_visibility,
)
from backend.phase1.analytics.organizational_intelligence_service import (
    build_organizational_intelligence,
)
from backend.phase1.analytics.coordination_intelligence_service import (
    build_project_coordination_intelligence,
)
from backend.phase1.analytics.decision_support_service import (
    build_project_decision_support,
)
from backend.phase1.analytics.operational_intelligence_service import (
    build_project_operational_intelligence,
)
from backend.phase1.auth.project_access import ProjectAccessService
from backend.phase1.dependencies.auth import get_project_access_service
from backend.phase1.schemas.operational_intelligence_schema import (
    OperationalIntelligenceRead,
)
from backend.phase1.schemas.executive_visibility_schema import (
    ExecutiveVisibilityRead,
)
from backend.phase1.schemas.organizational_intelligence_schema import (
    OrganizationalIntelligenceRead,
)
from backend.phase1.analytics.usage_store import append_usage_event
from backend.phase1.auth.auth import User
from backend.phase1.auth.dependencies import get_current_active_user
from backend.phase1.auth.operational_audit import log_operational_action
from backend.phase1.schemas.usage_event_schema import UsageEventCreate

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = logging.getLogger("betavanx.adoption_metrics")


def _require_adoption_reader(user: User) -> User:
    if user.role not in ("admin", "supervisor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Adoption summary is limited to admin and supervisor roles.",
        )
    return user


def _require_organizational_reader(user: User) -> User:
    if user.role not in ("admin", "supervisor", "investor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organizational intelligence is not available for this role.",
        )
    return user


def _require_executive_reader(user: User) -> User:
    if user.role not in ("admin", "investor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Executive operational visibility is limited to admin and investor roles.",
        )
    return user


@router.post("/usage-events", status_code=status.HTTP_201_CREATED)
def record_usage_event(
    payload: UsageEventCreate,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    record = append_usage_event(
        username=current_user.username,
        role=current_user.role,
        event_type=payload.event_type,
        page_path=payload.page_path,
        session_id=payload.session_id,
        referrer_path=payload.referrer_path,
        project_id=payload.project_id,
    )
    logger.info(
        "adoption_metric usage_event type=%s role=%s path=%s",
        payload.event_type,
        current_user.role,
        payload.page_path[:80],
    )
    return {"status": "recorded", "recorded_at": record["recorded_at"]}


@router.get("/adoption-summary")
def get_adoption_summary(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    _require_adoption_reader(current_user)
    db = None
    try:
        from backend.db.session import SessionLocal

        db = SessionLocal()
        summary = build_adoption_summary(db)
    except Exception:  # noqa: BLE001 — JSONL-only when DB unavailable
        summary = build_adoption_summary(None)
    finally:
        if db is not None:
            db.close()

    log_operational_action(
        current_user,
        "adoption_summary_read",
        mutation_category="query",
        detail={"event_count": summary["usage"]["event_count"]},
    )
    return summary


@router.get(
    "/projects/{project_id}/operational-intelligence",
    response_model=OperationalIntelligenceRead,
)
def get_project_operational_intelligence(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> OperationalIntelligenceRead:
    project_access.ensure_project_access(current_user, project_id)
    db = None
    try:
        from backend.db.session import SessionLocal

        db = SessionLocal()
        payload = build_project_operational_intelligence(db, project_id)
        payload["decision_support"] = build_project_decision_support(db, project_id)
        payload["coordination_intelligence"] = build_project_coordination_intelligence(
            db,
            project_id,
        )
    except Exception:  # noqa: BLE001
        payload = build_project_operational_intelligence(None, project_id)
        payload["decision_support"] = build_project_decision_support(None, project_id)
        payload["coordination_intelligence"] = build_project_coordination_intelligence(
            None,
            project_id,
        )
    finally:
        if db is not None:
            db.close()

    log_operational_action(
        current_user,
        "operational_intelligence_read",
        mutation_category="query",
        project_id=project_id,
        detail={
            "band": payload.get("health", {}).get("band"),
            "priority_count": len(
                (payload.get("decision_support") or {}).get("priority_queue", []),
            ),
            "coordination_band": (payload.get("coordination_intelligence") or {}).get(
                "coordination_band",
            ),
        },
    )
    return OperationalIntelligenceRead.model_validate(payload)


@router.get(
    "/organizational-intelligence",
    response_model=OrganizationalIntelligenceRead,
)
def get_organizational_intelligence(
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> OrganizationalIntelligenceRead:
    _require_organizational_reader(current_user)
    accessible = project_access.get_accessible_project_ids(current_user)
    db = None
    try:
        from backend.db.session import SessionLocal

        db = SessionLocal()
        payload = build_organizational_intelligence(db, accessible)
    except Exception:  # noqa: BLE001
        payload = build_organizational_intelligence(None, accessible)
    finally:
        if db is not None:
            db.close()

    log_operational_action(
        current_user,
        "organizational_intelligence_read",
        mutation_category="query",
        detail={
            "maturity_band": payload.get("maturity_band"),
            "projects_analyzed": payload.get("projects_analyzed"),
        },
    )
    return OrganizationalIntelligenceRead.model_validate(payload)


@router.get(
    "/executive-visibility",
    response_model=ExecutiveVisibilityRead,
)
def get_executive_visibility(
    current_user: User = Depends(get_current_active_user),
    project_access: ProjectAccessService = Depends(get_project_access_service),
) -> ExecutiveVisibilityRead:
    _require_executive_reader(current_user)
    accessible = project_access.get_accessible_project_ids(current_user)
    db = None
    try:
        from backend.db.session import SessionLocal

        db = SessionLocal()
        payload = build_executive_visibility(db, accessible)
    except Exception:  # noqa: BLE001
        payload = build_executive_visibility(None, accessible)
    finally:
        if db is not None:
            db.close()

    log_operational_action(
        current_user,
        "executive_visibility_read",
        mutation_category="query",
        detail={
            "portfolio_band": (payload.get("portfolio_health") or {}).get(
                "overall_band",
            ),
            "priority_count": len(payload.get("leadership_priorities", [])),
        },
    )
    return ExecutiveVisibilityRead.model_validate(payload)

"""Phase 1 pilot role policy — minimal route-level enforcement.

Maps pilot personas to existing in-memory roles:
  Project Manager / Site Supervisor / Engineer → admin or supervisor
  Worker → worker
  Investor / Viewer → investor

No persistence or domain logic; used only as FastAPI dependencies.
"""

from __future__ import annotations

from backend.phase1.auth.auth import (
    ROLE_ADMIN,
    ROLE_INVESTOR,
    ROLE_SUPERVISOR,
    ROLE_WORKER,
)
from backend.phase1.auth.dependencies import require_roles

# Planning creates (project, WBS, location, activity, step, work order)
require_planning_actor = require_roles(ROLE_ADMIN, ROLE_SUPERVISOR)

# Runtime mutations
require_work_order_assigner = require_roles(ROLE_ADMIN, ROLE_SUPERVISOR)
require_daily_report_submitter = require_roles(
    ROLE_ADMIN,
    ROLE_SUPERVISOR,
    ROLE_WORKER,
)
require_workflow_approver = require_roles(ROLE_ADMIN, ROLE_SUPERVISOR)

# Runtime reads — all authenticated pilot roles
require_runtime_reader = require_roles(
    ROLE_ADMIN,
    ROLE_SUPERVISOR,
    ROLE_WORKER,
    ROLE_INVESTOR,
)

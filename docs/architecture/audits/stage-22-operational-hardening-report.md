# Stage 22 — Operational Hardening Report

**Stage:** 22 — Operational Hardening  
**Type:** Runtime integrity and survivability (not redesign, not feature expansion)  
**Prerequisite:** Stage 21 persistence, work-order queries, pilot enhancements

---

## 1. Concurrency Protections Added

### Mechanism

Lightweight **optimistic locking** using existing `updated_at` timestamps (no new version column, no row-level locking framework).

| Component | Path |
| --- | --- |
| Exception | `backend/phase1/exceptions.py` — `ConcurrencyConflictError` |
| Helpers | `backend/phase1/repositories/optimistic.py` — `assert_unchanged`, `touch_updated_at` |
| Base repo | `BaseRepository.update(..., expected_updated_at=, resource_type=)` |

### Protected operations

| Entity | When enforced | Client token field |
| --- | --- | --- |
| WorkflowStep | Approve step (status update) | `expected_workflow_step_updated_at` |
| WorkOrder | Submit daily report (stale WO guard) | `expected_work_order_updated_at` |
| DailyReport | Update path ready (`DailyReportUpdate.expected_updated_at`) | Future PATCH |
| Approval | Create guarded by duplicate check + step lock on approve | Via step token |

### HTTP behavior

- `ConcurrencyConflictError` → **409 Conflict**
- Duplicate assignment/approval (Stage 21) → **409 Conflict**
- Logged under `mutation_category=conflict` via `log_concurrency_conflict`

### Frontend

- Approve and daily-report forms send `updated_at` from server lists when available.
- Optional tokens: omitting them preserves backward-compatible behavior (no lock check).

---

## 2. Audit Hardening Summary

### Enhanced logger: `betavanx.operational_audit`

| Field | Description |
| --- | --- |
| `occurred_at` | UTC ISO timestamp |
| `username` / `role` | Actor |
| `mutation_category` | `planning` \| `execution` \| `governance` \| `conflict` |
| `action` | Stable action name |
| `project_id` | Scope |
| `resource_type` / `resource_id` | Target entity |

### Coverage

| Action | Category |
| --- | --- |
| All planning POSTs | `planning` |
| assign_work_order, submit_daily_report | `execution` |
| approve_workflow_step | `governance` |
| Concurrency conflicts on assign/report/approve | `conflict` |

### Blocker resolution

`WorkflowGovernanceService.resolve_blocker` updates blockers; audit hook ready when a public API route is added (internal service path documented for Stage 23).

---

## 3. Runtime Freshness Strategy

### Evaluation

| Approach | Decision |
| --- | --- |
| WebSockets | **Deferred** — adds infra and connection management beyond Phase 1 pilot |
| SSE | **Deferred** — same |
| **Polling** | **Implemented** — minimal, no new state libraries |

### Implementation

| Piece | Detail |
| --- | --- |
| Hook | `frontend/lib/hooks/useRuntimePolling.ts` |
| Overview dashboard | 30s interval reload of `dashboard-summary` when loaded |
| Activity runtime | 45s interval reload of activity view + workflow-steps |

Users retain manual **Refresh dashboard**; polling reduces stale KPIs/blockers during multi-user sessions.

---

## 4. PostgreSQL Validation Results

### Scripts

| Script | Purpose |
| --- | --- |
| `backend/scripts/stage22_postgres_validation.py` | UUID, JSONB, pagination, membership 403, JSONB daily report |
| `backend/scripts/stage22_stress_review.py` | Query timing smoke + row-count notes |

### Environment (this audit run)

| Check | Result |
| --- | --- |
| PostgreSQL on localhost:5432 | **Unavailable** (connection refused) |
| Role-only CI scripts (19/21/22) | **Pass** with `SKIP_STARTUP_VALIDATION=true` |
| Full PG validation | **Not executed** — run locally with `RUN_POSTGRES_VALIDATION=true` |

### Commands (operator)

```bash
PYTHONPATH=. python backend/scripts/phase1_init_schema.py
# or: alembic -c backend/alembic.ini upgrade head
RUN_POSTGRES_VALIDATION=true PYTHONPATH=. python backend/scripts/stage22_runtime_verification.py
PYTHONPATH=. python backend/scripts/stage22_postgres_validation.py
PYTHONPATH=. python backend/scripts/stage22_stress_review.py
```

### Expected validations when DB is up

- UUID generation via `gen_random_uuid()`
- JSONB on `daily_reports.evidence_metadata`
- Transaction rollback per request (`get_db` commit/rollback)
- FK RESTRICT / CASCADE per integrity audit
- Unique constraints (project code, WO number per project, assignment junction)
- 409 on duplicate assign/approve and optimistic conflicts
- Paginated `work-orders` list shape
- Worker 403 on unauthorized project dashboard

---

## 5. Migration System Status

| Item | Status |
| --- | --- |
| Alembic config | `backend/alembic.ini` |
| Environment | `backend/alembic/env.py` (Phase 1 `Base.metadata`) |
| Baseline revision | `20260603_0001` — `project_memberships` table |
| Legacy bootstrap | `backend/scripts/phase1_init_schema.py` still valid for greenfield |
| Startup check | `backend/phase1/startup.py` — DB ping; optional `REQUIRE_ALEMBIC_HEAD=true` |
| App lifespan | `create_app()` calls `validate_startup()` unless `SKIP_STARTUP_VALIDATION` |

**Note:** Baseline migration adds `project_memberships` only. Existing deployments that used `create_all` already have core tables; run `alembic upgrade head` to align version table + membership DDL.

---

## 6. CI / Runtime Verification Status

| Script | Scope |
| --- | --- |
| `stage22_runtime_verification.py` | Orchestrates stage19 + stage21; optional PG via `RUN_POSTGRES_VALIDATION` |
| `stage19_pilot_validation.py` | Role matrix; DB-safe `_post_status` wrapper |
| `stage21_pilot_validation.py` | Work-order list + membership (DB optional) |
| `stage22_integrity_audit.py` | FK / delete policy documentation |

### Suggested CI job

```yaml
env:
  SKIP_STARTUP_VALIDATION: "true"
  PYTHONPATH: "."
steps:
  - run: python backend/scripts/stage22_runtime_verification.py
  - run: python backend/scripts/stage22_integrity_audit.py
  # Optional service container Postgres:
  - run: RUN_POSTGRES_VALIDATION=true python backend/scripts/stage22_runtime_verification.py
```

---

## 7. Stress-Review Findings

Audit-only script (`stage22_stress_review.py`) — no premature optimization.

| Risk | Finding | Mitigation (existing / planned) |
| --- | --- | --- |
| Large `daily_reports` | N+1 not in list endpoints; unbounded project WO list uses limit 200 | Keep pagination caps (max 200) |
| Dashboard refresh | Multiple aggregates per project | Acceptable for pilot; index on `project_id` present |
| Workflow-step options | N+1 activity→steps in frontend hook | Documented Stage 21 gap; batch API in Stage 23 |
| Stale reads | Mitigated by 30–45s polling | Sufficient for pilot |
| Progress recompute | `persist_workflow_step_progress` updates without client token | Internal; low collision risk |

---

## 8. Delete & Orphan Safety

| Control | Implementation |
| --- | --- |
| FK RESTRICT | Prevents deleting parents with operational children |
| `project_memberships` CASCADE | Membership removed with project delete (only if project delete ever allowed) |
| Junction CASCADE | `work_order_workflow_steps` cleans assignments |
| Repository delete guard | `delete_policy.py` — only `WorkOrderWorkflowStep`, `BOQMapping` |
| No public DELETE APIs | Phase 1 routers are create/read only |

Script: `python backend/scripts/stage22_integrity_audit.py`

---

## 9. Remaining Production Blockers

| Blocker | Severity |
| --- | --- |
| PostgreSQL not validated in CI without service container | High for production gate |
| Full Alembic autogen for all Phase 1 tables | Medium — baseline only adds memberships |
| No PATCH APIs for entity updates (optimistic tokens on creates/approve only) | Medium |
| Blocker resolve not exposed on runtime router | Low |
| Global supervisor/worker grant on assign (pilot) | Medium for real IAM |
| No rate limiting / connection pool tuning doc | Low |

---

## 10. Recommended Stage 23

1. **CI Postgres service** — mandatory `stage22_postgres_validation` in pipeline.
2. **Full Alembic autogen** — single revision matching DDL v1; retire `create_all` in production.
3. **Blocker resolve API** + audit on `resolve_blocker`.
4. **Batch workflow-step query** — remove N+1 in `useProjectWorkflowStepOptions`.
5. **Per-user project grants** — replace role-wide operational team grant.
6. **Optional:** ETag/`If-Match` header support mirroring `expected_*_updated_at` for API clients.

---

## 11. Key Files (reference)

**Backend**

- `phase1/exceptions.py`, `repositories/optimistic.py`, `repositories/base_repository.py`
- `integrity/delete_policy.py`, `auth/operational_audit.py`
- `phase1/startup.py`, `phase1/app.py`
- `alembic/`, `scripts/stage22_*.py`

**Frontend**

- `lib/hooks/useRuntimePolling.ts`
- `app/dashboard/overview/page.tsx`
- `app/dashboard/activity-instances/[activityInstanceId]/page.tsx`

**Stop:** Stage 22 complete per scope.

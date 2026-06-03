# Stage 21 — Persistence, Work-Order Query & Pilot Enhancements Report

**Stage:** 21 — Persistence, Work-Order Query & Pilot Enhancements  
**Type:** Backend persistence + query binding + pilot hardening (no UI redesign, no new domain entities, no runtime calculation changes)  
**Prerequisite:** Stage 20 frontend query binding + role-aware UI

---

## 1. Backend Persistence for Project Membership

### Implementation

| Component | Path | Purpose |
| --- | --- | --- |
| ORM table | `backend/phase1/models/project_membership.py` | `project_memberships` — `username`, `project_id`, `granted_at` |
| Repository | `backend/phase1/repositories/project_membership_repository.py` | `grant()`, `list_project_ids_for_username()` |
| Service | `backend/phase1/auth/project_access.py` | `ProjectAccessService` — replaces in-memory `_MEMBERSHIP` dict |
| DI | `backend/phase1/dependencies/auth.py` | `get_project_access_service()` |

### Grant rules (unchanged semantics, persisted)

| Event | Grants |
| --- | --- |
| `POST /planning/projects` | Creator + all `investor` accounts |
| `POST .../assign` | All `supervisor` + `worker` pilot accounts |
| `POST /runtime/daily-reports` | Submitting user |
| `admin` | All projects (`get_accessible_project_ids` → `None`) |

### Enforcement scope

- **Runtime:** all project-scoped GET/POST routes use `ProjectAccessService.ensure_project_access`.
- **Planning:** all create routes check membership on `project_id` (workflow step resolves project via activity).

### Schema bootstrap

```bash
PYTHONPATH=. python backend/scripts/phase1_init_schema.py
```

Creates `project_memberships` alongside existing Phase 1 tables via `Base.metadata.create_all`.

---

## 2. Work-Order Query Endpoints

### New endpoint

| HTTP | Path | Handler |
| --- | --- | --- |
| GET | `/runtime/projects/{project_id}/work-orders` | `list_work_orders` in `runtime_router.py` |

### Query parameters

| Parameter | Type | Behavior |
| --- | --- | --- |
| `status` | string | Filter `work_orders.status` |
| `workflow_step_id` | UUID | Inner join `work_order_workflow_steps` |
| `planned_date_from` / `planned_date_to` | date | Planned date range |
| `sort_by` | `planned_date` \| `created_at` | Default `planned_date` |
| `sort_dir` | `asc` \| `desc` | Default `desc` |
| `limit` / `offset` | int | Paginated (default limit 50, max 200) |

### Layering

```
runtime_router → RuntimeUseCases.list_work_orders
              → RuntimeQueryService.list_work_orders
              → WorkOrderRepository.list_filtered / count_filtered
```

Response: `PaginatedResponse[WorkOrderRead]` with `items`, `total`, `limit`, `offset`.

### Frontend binding

| Client | Consumer |
| --- | --- |
| `listWorkOrders()` in `frontend/lib/api/phase1/runtime.ts` | API wrapper |
| `useWorkOrders(projectId)` in `frontend/lib/hooks/usePhase1Lists.ts` | Console execution assign + daily report dropdowns |
| `WorkOrderListParams` in `types.ts` | Typed filters |

Execution page prefers server work orders; `WorkspaceContext` remains fallback for same-browser session creates.

---

## 3. Legacy API Cleanup

### Dashboard routes (Stage 20)

Legacy paths under `app/dashboard/{planning,daily-reports,...}` redirect to Phase 1 console/overview — unchanged.

### API barrel

`frontend/lib/api/index.ts` now exports **only** `apiRequest`, `ApiError`, `BASE_URL`. Removed re-exports of:

- `/dashboard` (`dashboard.ts`)
- `/lifecycle/*` (`lifecycle.ts`)
- `/workforce/*` (`workforce.ts`)

Active dashboard pages import `@/lib/api/phase1/*` exclusively.

### Orphan modules (retained on disk, not used by dashboard)

| Module | Status |
| --- | --- |
| `lib/api/dashboard.ts` | Orphan — legacy `backend/api.py` era |
| `lib/api/lifecycle.ts` | Orphan — task lifecycle prototype |
| `lib/api/workforce.ts` | Orphan — referenced only by unused dashboard components |
| `app/task/[taskId]` | Still uses `lib/api/tasks` (outside Stage 21 dashboard scope) |

**Note:** `backend/api.py` legacy FastAPI app is untouched (Phase 1 runs via `backend/phase1/app.py`).

---

## 4. Multi-User Pilot Enhancements

### Automated verification

| Script | Purpose |
| --- | --- |
| `backend/scripts/stage21_pilot_validation.py` | Role 403 matrix + work-order pagination shape + membership after project create (when DB up) |
| `backend/scripts/stage19_pilot_validation.py` | Still valid for role-only checks |

Run (from repo root, PostgreSQL required for full pass):

```bash
PYTHONPATH=. python backend/scripts/stage21_pilot_validation.py
```

### Operational audit logging

`backend/phase1/auth/operational_audit.py` — structured JSON lines on logger `betavanx.operational_audit` for:

- `create_project`, `create_wbs_item`, `create_location`, `create_activity_instance`, `create_workflow_step`, `create_work_order`
- `assign_work_order`, `submit_daily_report`, `approve_workflow_step`

### Duplicate alerts

`backend/phase1/auth/operational_alerts.py` — warning logs for:

- Duplicate work-order → workflow-step assignment (`WorkflowExecutionService`) → HTTP **409**
- Duplicate approval of same type on a step (`WorkflowGovernanceService`) → HTTP **409**

Runtime router maps `ValueError` messages starting with `Duplicate` to 409.

---

## 5. Pagination / Filter Validation

| Endpoint | Validated fields | Status |
| --- | --- | --- |
| `GET /runtime/projects` | limit, offset, total | Stage 17/20 |
| `GET .../activity-instances` | filters + pagination | Stage 17/20 |
| `GET .../work-orders` | status, workflow_step_id, date range, sort, pagination | **Stage 21** |
| `GET .../workflow-steps` | status, ready, pagination | Stage 17/20 |
| `GET .../daily-reports` | date range, status, pagination | Stage 17/20 |

Automated shape check in `stage21_pilot_validation.py` when DB returns 200.

---

## 6. Role Enforcement Matrix

Backend `role_policy.py` unchanged. Frontend `role-policy.ts` + `RoleGate` unchanged from Stage 20.

| Action | admin | supervisor | worker | investor |
| --- | --- | --- | --- | --- |
| Planning POST | Y | Y | N | N |
| Runtime GET (incl. work-orders list) | Y | Y | Y* | Y* |
| Assign | Y | Y | N | N |
| Daily report | Y | Y | Y | N |
| Approve | Y | Y | N | N |

\*Only for projects in `project_memberships` (or all projects for admin).

---

## 7. Dashboard / Runtime Validation

| Surface | Data source | Stage 21 change |
| --- | --- | --- |
| Overview | `GET .../dashboard-summary` | Unchanged; manual **Refresh dashboard** reloads server KPIs |
| Activity runtime | `GET activity-instances/{id}` + workflow-steps query | Unchanged |
| Console execution | `listWorkOrders` for WO pickers | **Server-backed work orders** |
| Project picker | `listProjects` (membership-filtered) | Reads **persisted** membership |

Dashboard blockers/approvals on activity runtime still come from `listWorkflowSteps` operational rows (Stage 20).

---

## 8. Remaining Gaps & Stage 22 Recommendations

| Gap | Impact | Recommendation |
| --- | --- | --- |
| No `GET` list for WBS / locations | Planning dropdowns still use `WorkspaceContext` | Add query endpoints or expand planning read API |
| Activity runtime WO assignments | No assignment list endpoint; workspace fallback for labels | Expose assignments via runtime query or enrich work-order list DTO |
| `listDailyReports` not wired in UI | Report counts on activity page session-only | Bind per work order in activity runtime |
| Legacy `lib/api/*.ts` files on disk | Confusion for new contributors | Delete or move to `legacy/` folder in Stage 22 |
| Pilot accounts in `_USERS` | Operational team grant is all supervisors/workers globally | Per-project role assignment table when real IAM exists |
| No Alembic migrations | `create_all` only | Introduce versioned migrations for production |
| E2E browser tests | Manual pilot only | Playwright persona suite against shared DB |
| Real-time push | Refresh required | Optional SSE/polling in Stage 22+ |

### Suggested Stage 22 focus

1. WBS/location query endpoints + frontend binding (remove workspace for planning).
2. Alembic migration for `project_memberships` and pilot seed data.
3. Assignment read model for activity runtime (server-backed WO/step links).
4. Delete orphan legacy frontend API modules; document Phase 1-only integration.
5. CI job: `stage21_pilot_validation.py` + `stage19_pilot_validation.py` against test Postgres.

---

## 9. Verification Summary

| Check | Result |
| --- | --- |
| Persisted `project_memberships` | Implemented |
| Planning + runtime project access | Implemented |
| `GET .../work-orders` with filters/pagination | Implemented |
| Frontend `useWorkOrders` on execution console | Implemented |
| Legacy dashboard API barrel removed | Implemented |
| Audit logging on mutating routes | Implemented |
| Duplicate assign/approve → 409 + alert log | Implemented |
| `stage21_pilot_validation.py` | Role checks pass without DB; full pass requires PostgreSQL |
| Local DB in audit session | Not running — connection refused on port 5432 |

---

## 10. Key Files (reference)

**Backend**

- `models/project_membership.py`, `repositories/project_membership_repository.py`
- `auth/project_access.py`, `auth/operational_audit.py`, `auth/operational_alerts.py`
- `repositories/work_order_repository.py` (filtered list)
- `routers/runtime_router.py`, `routers/planning_router.py`
- `scripts/phase1_init_schema.py`, `scripts/stage21_pilot_validation.py`

**Frontend**

- `lib/api/phase1/runtime.ts`, `lib/hooks/usePhase1Lists.ts`
- `app/dashboard/console/execution/page.tsx`
- `lib/api/index.ts`

**Stop:** Stage 21 complete per scope.

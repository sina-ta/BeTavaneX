# Stage 17 — Operational Query Layer Report

**Stage:** 17 — Operational Query Layer  
**Scope:** Phase 1 backend read-only listing, filtering, pagination, and enriched dashboard summary. No new entities, no Runtime Core changes (ProgressService, WorkflowExecutionService, WorkflowGovernanceService untouched), no frontend changes.

---

## 1. Endpoints Implemented

| Method | Path | Response |
| --- | --- | --- |
| `GET` | `/runtime/projects` | `PaginatedResponse[ProjectRead]` |
| `GET` | `/runtime/projects/{project_id}/activity-instances` | `PaginatedResponse[ActivityInstanceRead]` |
| `GET` | `/runtime/activity-instances/{activity_instance_id}/workflow-steps` | `PaginatedResponse[WorkflowStepOperationalRead]` |
| `GET` | `/runtime/work-orders/{work_order_id}/daily-reports` | `PaginatedResponse[DailyReportRead]` |
| `GET` | `/runtime/projects/{project_id}/dashboard-summary` | `ProjectDashboardSummaryRead` |

**Preserved (unchanged paths):**

| Method | Path | Notes |
| --- | --- | --- |
| `GET` | `/runtime/projects/{project_id}/dashboard` | Existing compact KPI summary |
| `GET` | `/runtime/activity-instances/{activity_instance_id}` | Existing runtime view |
| `POST` | `/runtime/work-orders/{work_order_id}/assign` | Execution |
| `POST` | `/runtime/daily-reports` | Execution |
| `POST` | `/runtime/workflow-steps/{workflow_step_id}/approve` | Governance |

All endpoints remain behind the existing router-level Bearer auth (`get_current_active_user`).

---

## 2. Query Parameters Supported

### `GET /runtime/projects`

| Parameter | Type | Purpose |
| --- | --- | --- |
| `name` | string | Case-insensitive partial match on `name` or `code` |
| `status` | string | Exact status filter |
| `planned_start_from` / `planned_start_to` | date | Planned start range |
| `planned_finish_from` / `planned_finish_to` | date | Planned finish range |
| `sort_by` | `planned_start` \| `created_at` | Sort field (default `created_at`) |
| `sort_dir` | `asc` \| `desc` | Sort direction (default `desc`) |
| `limit` | int | Page size, 1–200 (default 50) |
| `offset` | int | Page offset (default 0) |

### `GET /runtime/projects/{project_id}/activity-instances`

| Parameter | Type | Purpose |
| --- | --- | --- |
| `wbs_item_id` | UUID | Filter by WBS item |
| `location_id` | UUID | Filter by location |
| `status` | string | Exact status filter |
| `sort_by` | `planned_start` \| `created_at` | Default `created_at` |
| `sort_dir` | `asc` \| `desc` | Default `desc` |
| `limit` / `offset` | int | Pagination |

### `GET /runtime/activity-instances/{activity_instance_id}/workflow-steps`

| Parameter | Type | Purpose |
| --- | --- | --- |
| `status` | string | Exact workflow-step status |
| `ready` | bool | Filter by ready flag |
| `sort_by` | `planned_start` \| `progress_percent` \| `created_at` | Default `created_at` |
| `sort_dir` | `asc` \| `desc` | Default `desc` |
| `limit` / `offset` | int | Pagination |

Each item returns `WorkflowStepOperationalRead`: `workflow_step` (`WorkflowStepRead`), `approvals` (`ApprovalRead[]`), `blockers` (`BlockerRead[]`).

### `GET /runtime/work-orders/{work_order_id}/daily-reports`

| Parameter | Type | Purpose |
| --- | --- | --- |
| `status` | string | Report status filter |
| `report_date_from` / `report_date_to` | date | Report date range |
| `sort_by` | `report_date` \| `created_at` | Default `report_date` |
| `sort_dir` | `asc` \| `desc` | Default `desc` |
| `limit` / `offset` | int | Pagination |

Response items are `DailyReportRead` including `evidence_metadata` (read-only JSONB field).

### `GET /runtime/projects/{project_id}/dashboard-summary`

No query parameters. Returns aggregated read-only summary (see §4).

---

## 3. Pagination & Filter Behavior

- **Envelope:** All list endpoints return `PaginatedResponse[T]` with `items`, `total`, `limit`, `offset`.
- **`total`:** Computed via repository `count_filtered` using the same filter predicates as the list query (not an estimate).
- **Defaults:** `limit=50`, `offset=0`; `limit` capped at **200** in the router.
- **Sorting:** Applied in the repository layer via SQL `ORDER BY` on the requested column; no in-memory sort after fetch.
- **Name search (projects):** `ILIKE '%{name}%'` on both `name` and `code` (PostgreSQL-oriented; matches existing stack).
- **Workflow-step list:** For each page of steps, approvals and blockers are loaded per step via existing `ApprovalRepository.list` / `BlockerRepository.list` (scoped by `workflow_step_id`). No new business rules; read-only assembly in `RuntimeQueryService`.

---

## 4. Runtime Dashboard Integration

### Existing: `GET /runtime/projects/{project_id}/dashboard`

Unchanged contract: `project_id`, `project_progress`, `activity_instance_count`, `workflow_step_count`, `work_order_count`.

Implementation detail: `get_project_runtime_summary` now uses `ActivityInstanceRepository.list_filtered` + `WorkflowStepRepository.count_filtered` instead of loading all activity instances globally and filtering in Python.

### New: `GET /runtime/projects/{project_id}/dashboard-summary`

`ProjectDashboardSummaryRead` extends the compact dashboard with:

| Field | Source |
| --- | --- |
| `project_id`, `project_progress`, counts | Same as compact dashboard (`ProgressService` + repositories) |
| `activity_instances[]` | Per-instance `code`, `name`, `status`, `progress_percent` via `ProgressService.calculate_activity_instance_progress` |
| `work_orders_by_status[]` | Count of work orders grouped by `status` for the project |

Read-only; no writes or state transitions.

---

## 5. Verification Results

| Check | Result |
| --- | --- |
| `from backend.phase1.app import app` | **Pass** |
| Runtime router route count | **10** routes registered |
| Runtime paths enumerated | All 5 new query paths present alongside existing dashboard/execution routes |
| Direct ORM in routers | **None** — routers delegate only to `RuntimeUseCases` |
| Runtime Core services modified | **None** (`ProgressService`, `WorkflowExecutionService`, `WorkflowGovernanceService` unchanged) |

**Layering (Stage 17 additions):**

```
Router → RuntimeUseCases (thin delegates) → RuntimeQueryService (read assembly) → Repositories (filtered SQL)
```

**Files touched:**

| Area | Files |
| --- | --- |
| Repositories | `project_repository.py`, `activity_instance_repository.py`, `workflow_step_repository.py`, `daily_report_repository.py` |
| Read service | `runtime_query_service.py` (operational list + dashboard-summary methods; `ProjectRepository` injected) |
| Application | `runtime_use_cases.py` (delegate methods only) |
| DI | `dependencies/services.py` (`project_repository` passed into `RuntimeQueryService`) |
| Router | `runtime_router.py` |
| Schemas | `pagination_schema.py`, `blocker_schema.py`, `runtime_query_schema.py`, `schemas/__init__.py` |

**Not run this session:** Full PostgreSQL integration test or authenticated HTTP e2e (no in-repo harness). Recommend `next` manual smoke: login → `GET /runtime/projects` → list activities → list steps → list reports → `GET .../dashboard-summary`.

---

## 6. Remaining Operational Gaps

1. **No `GET` list for work orders** — only daily reports under a known `work_order_id`; project-scoped work-order listing still absent.
2. **No global search** — filters are per-endpoint; no cross-entity full-text search.
3. **Workflow-step list N+1 reads** — approvals/blockers fetched per step on the current page (acceptable for small pages; may need batching at scale).
4. **Dashboard-summary activity list unbounded** — uses `limit=10_000` internally for progress aggregation; fine for Phase 1 demos, not for very large projects without pagination on the summary itself.
5. **Frontend not wired** — Stage 17 is backend-only per scope; `WorkspaceContext` / manual UUID flows in the UI remain until Stage 18 (or equivalent) binds these endpoints.
6. **No `GET` by id for project / work order** — only list and existing composite views.

---

## Recommended Next Stage

**Stage 18 — Frontend Operational Binding:** Add Phase 1 client wrappers for the five new query endpoints; replace session-registry pickers with server-backed lists; use `dashboard-summary` on the command center; keep layouts unchanged.

**Stopping after Stage 17 as instructed.**

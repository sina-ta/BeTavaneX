# Stage 20 — Frontend Query Binding + Role-Aware UI Report

**Stage:** 20 — Frontend Query Binding + Role-Aware UI  
**Type:** Integration and enforcement (no UI redesign, no new backend entities/endpoints)  
**Prerequisite:** Stage 17 Operational Query Layer, Stage 19 multi-user pilot + backend `require_roles()`

**Pilot personas (unchanged from Stage 19):**

| Persona | Account | Password |
| --- | --- | --- |
| Project Manager | `admin` | `admin` |
| Site Supervisor | `supervisor` | `supervisor` |
| Worker | `worker` | `worker` |
| Investor / Viewer | `investor` | `investor` |

---

## 1. Endpoints Mapped

All Stage 17 query routes are bound in `frontend/lib/api/phase1/runtime.ts` with typed DTOs from `frontend/lib/api/phase1/types.ts`.

| HTTP | Path | Client function | Primary UI consumer |
| --- | --- | --- | --- |
| GET | `/runtime/projects` | `listProjects` | `ProjectContext.refreshAuthorizedProjects`, console project picker |
| GET | `/runtime/projects/{project_id}/activity-instances` | `listActivityInstances` | `useActivityInstances`, console activity registry, workflow-step options |
| GET | `/runtime/activity-instances/{id}/workflow-steps` | `listWorkflowSteps` | `useWorkflowSteps`, activity runtime page, `useProjectWorkflowStepOptions` |
| GET | `/runtime/work-orders/{id}/daily-reports` | `listDailyReports` | Available for execution/runtime (not yet used in all cards) |
| GET | `/runtime/projects/{project_id}/dashboard-summary` | `getProjectDashboardSummary` | `/dashboard/overview` KPIs and activity list |
| GET | `/runtime/activity-instances/{id}` | `getActivityInstanceRuntime` | `/dashboard/activity-instances/[id]` |
| GET | `/runtime/projects/{project_id}/dashboard` | `getProjectDashboard` | Exported; overview uses `dashboard-summary` |
| POST | `/runtime/work-orders/{id}/assign` | `assignWorkOrder` | Console execution |
| POST | `/runtime/daily-reports` | `submitDailyReport` | Console execution |
| POST | `/runtime/workflow-steps/{id}/approve` | `approveWorkflowStep` | Console execution + activity runtime |

Planning writes remain in `frontend/lib/api/phase1/planning.ts` (UUID-based Phase 1 paths). Legacy numeric-ID and pre-Phase-1 paths (`/dashboard`, `/lifecycle`, `/workforce` under `frontend/lib/api/`) are **not** used by dashboard app routes; those modules remain in the repo for unused components only.

---

## 2. Role Enforcement Matrix

**Backend (authoritative):** `backend/phase1/auth/role_policy.py` — unchanged from Stage 19.

**Frontend (UX only):** `frontend/lib/auth/role-policy.ts`, `frontend/components/auth/RoleGate.tsx`, `frontend/app/dashboard/console/layout.tsx`, `frontend/lib/navigation.ts`.

| Capability | admin | supervisor | worker | investor |
| --- | --- | --- | --- | --- |
| Planning POST (project, WBS, location, activity, step, WO) | UI + API | UI + API | Hidden / 403 | Hidden / redirect overview |
| Runtime GET (lists, dashboards, activity view) | Yes | Yes | Yes | Yes |
| Assign work order | UI + API | UI + API | Hidden | Hidden |
| Submit daily report | UI + API | UI + API | UI + API | Hidden |
| Approve workflow step | UI + API | UI + API | Hidden message + 403 | Hidden |
| Operational Console hub (`/dashboard/console`) | Yes | Yes | Redirect → execution | Redirect → overview |
| Sidebar: planning / work orders | Yes | Yes | Reports only | Overview only |
| Approve on activity runtime page | Button | Button | “Not available for your role” | Same as worker |

**Forbidden UX patterns:**

- `RoleGate` — planning/assign/report/approve forms not rendered for disallowed roles.
- Console layout — investor blocked from console; worker blocked from planning hub.
- Activity runtime — approve button gated with `canApproveSteps()`.
- API failures still surface as error text (403 from server).

---

## 3. Project Scoping Validation

**Backend:** `backend/phase1/auth/project_access.py` (in-memory membership, pilot-only).

| Event | Who gains access |
| --- | --- |
| `POST /planning/projects` | Creator; all `investor` accounts |
| `POST .../assign` | All `supervisor` and `worker` accounts |
| `POST /runtime/daily-reports` | Submitting user |
| `admin` | All projects (`get_accessible_project_ids` → `None`) |

Runtime list/detail routes call `ensure_project_access`; `GET /runtime/projects` filters by membership in `runtime_query_service`.

**Frontend:** `frontend/lib/context/ProjectContext.tsx`

- Loads authorized projects via `listProjects` (server-filtered).
- Persists `selectedProjectId` in `localStorage` but **clears** selection if ID not in authorized list.
- `setSelectedProjectId` rejects IDs not in the current authorized set when list is `ready`.
- Console/overview call `refreshAuthorizedProjects()` after project create so pickers stay aligned.

**Limitations (documented gaps):**

- Membership resets on API process restart (not persisted to PostgreSQL).
- UI can still show stale `WorkspaceContext` entities from another browser session until refresh; server queries enforce scope on read/write.
- Deep-linking an activity UUID from another project returns **403** from API; UI should show error via `AsyncPageContent`.

---

## 4. Dashboard and Runtime View Status

| Surface | Data source | Status |
| --- | --- | --- |
| `/dashboard/overview` | `getProjectDashboardSummary` + authorized project picker | Wired; links to activity runtime by UUID |
| `/dashboard/activity-instances/[id]` | `getActivityInstanceRuntime` + `listWorkflowSteps` | Wired; approvals/blockers from operational rows; approve role-gated |
| `/dashboard/console` | Planning POST + `ProjectContext` | Role-gated planning; server project list |
| `/dashboard/console/activity` | `listActivityInstances`, server step options | Registry from query layer |
| `/dashboard/console/execution` | Assign/report/approve POST + `useProjectWorkflowStepOptions` | Role-gated forms |

**Activity runtime enrichments (Stage 20):**

- Merges `WorkflowStepOperationalRead` approvals and blockers per step.
- Work order / daily report lines still use `WorkspaceContext` for assignment labels (no project-scoped work-order list endpoint in Stage 17).

---

## 5. Remaining Frontend Gaps

| Gap | Impact | Suggested owner stage |
| --- | --- | --- |
| No `GET /runtime/projects/{id}/work-orders` | Execution forms and runtime WO cards rely on session `WorkspaceContext` | Stage 21+ (needs new endpoint — out of Stage 20 scope) |
| No list endpoints for WBS / locations | Planning dropdowns use workspace registry, not query layer | Stage 21+ |
| `listDailyReports` unused in activity cards | Report counts on runtime page are workspace-only | Wire when WO list exists or per-assignment fetch |
| Dead code: `lib/api/dashboard.ts`, `lifecycle.ts`, `workforce.ts` | Unused by app routes; legacy components may still import | Cleanup pass |
| No automated Playwright/Cypress persona suite | Manual pilot only | Stage 21 QA |
| Investor sees empty project list until a project is created | By design (investors granted on create) | Document in pilot scripts |

---

## 6. Multi-User Execution Notes

**Recommended pilot (two browsers, shared PostgreSQL):**

1. **admin** — login → create project → refresh projects → select project → create WBS/location/activity/step/WO via console.
2. **supervisor** — after assign on that project, should see project in picker → assign WO → approve step.
3. **worker** — after assign or own report submit, sees project → submit daily report only; planning/approve hidden.
4. **investor** — sees project after create → overview dashboard read-only; console redirects to overview.
5. **Cross-user** — B refreshes overview after A’s approve; progress KPIs update from `dashboard-summary`.

**Concurrency:**

- No WebSocket; refresh pages after writes.
- `WorkspaceContext` is per-tab; multi-user dropdown labels may lag until server list hooks replace workspace for WBS/location/WO.

**Automated checks:**

- Stage 19 script: `backend/scripts/stage19_pilot_validation.py` (role 403 matrix).
- Stage 20 adds project 403 when accessing another user’s project UUID (manual or extend script).

---

## 7. Legacy Cleanup

| Legacy route | Redirect target |
| --- | --- |
| `/dashboard/planning` | `/dashboard/console` |
| `/dashboard/daily-reports` | `/dashboard/console/execution` |
| `/dashboard/daily-work-orders` | `/dashboard/console/execution` |
| `/dashboard/performance` | `/dashboard/overview` |
| `/dashboard/workers` | `/dashboard/overview` |
| `/dashboard/workforce` | `/dashboard/overview` |

Sidebar and main dashboard flows use Phase 1 paths only (`/dashboard/overview`, `/dashboard/console/*`).

---

## 8. Verification Summary

| Check | Result |
| --- | --- |
| Query client maps all five Stage 17 list/summary endpoints | Done |
| Typed DTOs for paginated + operational reads | Done |
| Role gates on console + navigation + runtime approve | Done |
| Project picker backed by `GET /runtime/projects` | Done |
| Overview uses `dashboard-summary` | Done |
| Activity runtime uses query workflow-steps + role approve | Done |
| Legacy dashboard routes redirect | Done |
| Full e2e with live DB in CI | Not run in this session |
| `tsc --noEmit` | Attempted; environment did not return output — run locally before release |

---

## 9. Recommended Stage 21

1. **Persist project membership** in PostgreSQL (replace in-memory `project_access.py`).
2. **Add query endpoints** for work orders (and optionally WBS/locations) per project — then remove workspace dependency for execution dropdowns and runtime WO panels.
3. **Wire `listDailyReports`** on activity runtime when work orders are server-listed.
4. **Remove or quarantine** legacy `frontend/lib/api/{dashboard,lifecycle,workforce}.ts` exports from `lib/api/index.ts`.
5. **Pilot automation** — scripted multi-browser flow or API integration test covering project scoping + role matrix.

---

## 10. Files Touched (reference)

**Frontend (binding + roles):**

- `lib/api/phase1/runtime.ts`, `types.ts`, `index.ts`
- `lib/auth/role-policy.ts`, `lib/auth/index.ts`
- `lib/context/ProjectContext.tsx`
- `lib/hooks/usePhase1Lists.ts`
- `lib/navigation.ts`
- `components/auth/RoleGate.tsx`, `components/layout/Sidebar.tsx`
- `app/dashboard/overview/page.tsx`
- `app/dashboard/console/**`, `app/dashboard/console/layout.tsx`
- `app/dashboard/activity-instances/[activityInstanceId]/page.tsx`
- Legacy redirects under `app/dashboard/{planning,daily-reports,...}/page.tsx`

**Backend (project scoping — minimal, no new entities):**

- `backend/phase1/auth/project_access.py`
- `runtime_router.py`, `planning_router.py`, `runtime_query_service.py`, `project_repository.py`

**Stop:** Stage 20 complete per scope. No UI redesign, no new state libraries, no new Phase 1 entities.

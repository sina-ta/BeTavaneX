# BetavanX Stage 16A — Phase 1 Integration Layer

**Objective:** Connect the existing frontend to the verified Phase 1 backend by
replacing legacy API integration with a typed Phase 1 integration layer.
**Constraints honored:** No UI redesign, no page rebuilds, no styling changes,
no backend changes, no React Query / Redux / Zustand, single shared HTTP client.
**Date:** 2026-06-02

---

## 1. Files Created

| File | Purpose |
|------|---------|
| `frontend/lib/api/phase1/types.ts` | UUID-based TypeScript DTOs mirroring backend Pydantic schemas (Project, WBSItem, Location, ActivityInstance, WorkflowStep, WorkOrder, DailyReport, Approval, WorkOrderWorkflowStep), runtime views (`ProjectDashboard`, `ActivityInstanceRuntimeView`), Create payloads, auth types, and a `toNumber` Decimal normalizer. |
| `frontend/lib/api/phase1/auth.ts` | OAuth2 password flow against `POST /auth/token` (form-encoded) using the shared `apiRequest`; client-side JWT claim decode (`sub`, `role`); `signIn`/`signOut` that persist token + role + username. |
| `frontend/lib/api/phase1/planning.ts` | Typed wrappers over the six `/planning/*` create endpoints. |
| `frontend/lib/api/phase1/runtime.ts` | Typed wrappers over the five `/runtime/*` endpoints (project dashboard, activity-instance view, assign work order, submit daily report, approve workflow step). |
| `frontend/lib/api/phase1/index.ts` | Barrel re-exporting the Phase 1 auth / planning / runtime / types surface. |
| `frontend/lib/context/ProjectContext.tsx` | Lightweight React Context (`ProjectProvider`, `useProject`) holding `selectedProjectId` / `setSelectedProjectId`, persisted to localStorage. No Redux/Zustand. |
| `frontend/app/dashboard/activity-instances/[activityInstanceId]/page.tsx` | New UUID-keyed activity runtime view consuming `GET /runtime/activity-instances/{id}`, rendered entirely with existing components. |

## 2. Files Modified

| File | Change |
|------|--------|
| `frontend/lib/auth/session.ts` | Added role/username storage (`getAuthRole`/`setAuthRole`, `getAuthUsername`/`setAuthUsername`); token now mirrored into an `auth_token` cookie (so middleware can read it) and cleared on logout; `isAuthenticated()` now token-based; `clearSession()` clears role/username. |
| `frontend/lib/auth/auth-client.ts` | Replaced the placeholder stub with a real facade delegating to `signIn`/`signOut`; aligned `UserRole` to Phase 1 roles (`admin`/`supervisor`/`worker`/`investor`). |
| `frontend/lib/auth/index.ts` | Re-exported the new session helpers. |
| `frontend/app/login/page.tsx` | Wired the form to `signIn` (real `POST /auth/token`); added submitting + error states; relabeled identifier field to "Username" and switched input type `email → text` (layout/styling unchanged). |
| `frontend/middleware.ts` | Re-enabled the route guard: protected paths (`/dashboard`, `/task`) require the `auth_token` cookie; unauthenticated requests redirect to `/login?redirect=…`. |
| `frontend/app/dashboard/layout.tsx` | Wrapped the shell in `ProjectProvider`. |
| `frontend/app/dashboard/overview/page.tsx` | Replaced the legacy `GET /dashboard` load with `GET /runtime/projects/{project_id}/dashboard` (project-scoped via `useProject`); added a project selector and an activity-runtime lookup; mapped the runtime summary into existing `KpiCard`/`KPIGrid`/`ProgressBar`/`CompactCard` components. |

## 3. API Mappings Completed

| Backend endpoint | Frontend function | Consumed by |
|------------------|-------------------|-------------|
| `POST /auth/token` | `phase1/auth.signIn` → `requestAccessToken` | Login page, auth facade |
| `POST /planning/projects` | `phase1/planning.createProject` | API layer (ready) |
| `POST /planning/wbs-items` | `phase1/planning.createWBSItem` | API layer (ready) |
| `POST /planning/locations` | `phase1/planning.createLocation` | API layer (ready) |
| `POST /planning/activity-instances` | `phase1/planning.createActivityInstance` | API layer (ready) |
| `POST /planning/workflow-steps` | `phase1/planning.createWorkflowStep` | API layer (ready) |
| `POST /planning/work-orders` | `phase1/planning.createWorkOrder` | API layer (ready) |
| `GET /runtime/projects/{id}/dashboard` | `phase1/runtime.getProjectDashboard` | **Overview dashboard** |
| `GET /runtime/activity-instances/{id}` | `phase1/runtime.getActivityInstanceRuntime` | **Activity runtime page** |
| `POST /runtime/work-orders/{id}/assign` | `phase1/runtime.assignWorkOrder` | API layer (ready) |
| `POST /runtime/daily-reports` | `phase1/runtime.submitDailyReport` | API layer (ready) |
| `POST /runtime/workflow-steps/{id}/approve` | `phase1/runtime.approveWorkflowStep` | API layer (ready) |

All eight requested DTOs are typed with **UUID string** identifiers; no numeric-ID
assumptions exist in the Phase 1 layer. Decimal fields are tolerant of
number/string serialization via `toNumber`.

## 4. Legacy Integrations Removed

- **Overview dashboard:** removed the legacy `getDashboardData()` (`GET /dashboard`)
  dependency and its legacy `DashboardData` mapping; the page is now driven solely
  by the Phase 1 runtime summary.
- **Fake authentication:** removed the localStorage-only "login" (`setSessionActive`
  with no API) and the placeholder `auth-client` token stub.
- **Role vocabulary drift:** legacy `manager/engineer/viewer` roles replaced with the
  backend's `admin/supervisor/worker/investor`.

> Out of scope / intentionally untouched (to honor "do not rebuild pages"): the
> legacy clients still used by other pages — `lib/api/{dashboard,reports,tasks,
> lifecycle,validation,analytics,workforce}.ts` and the pages `daily-reports`,
> `daily-work-orders`, `performance`, `workers`, `workforce`, `task/[taskId]`.
> These remain on legacy endpoints and are listed under Remaining Gaps.

## 5. Authentication Status

**Functional.** Login performs a real OAuth2 password grant against `POST /auth/token`,
decodes the JWT (`sub`, `role`), and persists `access_token` + `role` + `username`.
`apiRequest` injects `Authorization: Bearer <token>` on every subsequent call.
Demo credentials (from the backend in-memory registry): `admin/admin`,
`supervisor/supervisor`, `worker/worker`, `investor/investor`.

## 6. Route Protection Status

**Enabled.** `middleware.ts` enforces the `auth_token` cookie on `/dashboard/*`
and `/task/*`; unauthenticated users are redirected to `/login?redirect=…`. The
token is mirrored into the cookie at sign-in and removed at logout. (The cookie is
written by client JS and is therefore not `HttpOnly` — see Remaining Gaps for the
production hardening note.)

## 7. Dashboard Integration Status

**Integrated.** `/dashboard/overview` reads `GET /runtime/projects/{project_id}/dashboard`,
scoped by `ProjectContext`. The runtime summary (`project_progress`,
`activity_instance_count`, `workflow_step_count`, `work_order_count`) is mapped into
the existing KPI command-center UI (`KpiCard`, `KPIGrid`, `ProgressBar`, `CompactCard`,
`PageHeader`, `SectionContainer`) — no new visual design. A project selector is shown
when no project is chosen.

## 8. Runtime Integration Status

**Integrated.** The new `/dashboard/activity-instances/[activityInstanceId]` page reads
`GET /runtime/activity-instances/{id}` and renders the activity, its workflow steps,
and per-step progress (`progress_summary.workflow_step_progress`) using existing
components (`KpiCard`, `StatusBadge`, `ProgressBar`, `CompactCard`). It is reachable
from the dashboard's activity-runtime lookup.

## 9. Remaining Frontend Gaps Before Production

1. **No project/list discovery.** The backend exposes only `POST` for planning and
   `GET`-by-id for runtime; there is no `GET /planning/projects` list. The UI requires
   the user to paste a project UUID. A list/search endpoint (or a planning-driven
   project picker) is needed for usable navigation.
2. **Legacy pages still on legacy endpoints.** `daily-reports`, `daily-work-orders`,
   `performance`, `workers`, `workforce`, and `task/[taskId]` (numeric IDs) are not yet
   migrated to Phase 1 and will fail against the Phase 1 backend.
3. **No write-path UI yet.** Planning creates, work-order assignment, daily-report
   submission, and workflow-step approval are wired in the API layer but not surfaced
   in the UI (no forms).
4. **Cookie hardening.** `auth_token` is a JS-set, non-`HttpOnly` cookie for dev
   integration; production should issue an `HttpOnly`/`Secure` cookie (ideally
   server-set) and add CSRF protection.
5. **Token expiry / refresh.** No refresh endpoint exists; expired tokens require
   re-login. Client-side 401 handling (auto-redirect to login) is not yet centralized
   in `apiRequest`.
6. **i18n for new views.** The new overview and activity pages use literal English
   strings; they are not yet wired into the `en/fa` i18n system.
7. **Role-based UI gating.** Role is stored but not yet used to show/hide actions
   (admin/supervisor/worker/investor).
8. **Build verification pending.** IDE TypeScript diagnostics are clean for all created
   and modified files; a full `next build` / `tsc --noEmit` pass should be run once the
   shell environment is available (it was unavailable during this stage).

---

*Stage 16A complete. No backend changes. No commits.*

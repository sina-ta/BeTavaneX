# Stage 16B — Vertical Slice UI Execution Report

**Stage:** 16B — Vertical Slice UI Execution
**Scope:** Execute the complete Planning → Execution → Runtime vertical slice entirely from the frontend UI, using the verified Phase 1 backend and the integration layer delivered in Stage 16A.
**Constraints honored:** No UI redesign, no architecture rework, no new state libraries (Redux/Zustand/React Query), no backend changes, no new backend endpoints. Existing component system and CSS design system reused throughout.

---

## 1. Files Created

| File | Purpose |
| --- | --- |
| `frontend/lib/context/WorkspaceContext.tsx` | Session-scoped registry of every entity the user creates (projects, WBS items, locations, activity instances, workflow steps, work orders, assignments, daily reports, approvals). Persisted to `localStorage`. Exists because the Phase 1 backend exposes **no list endpoints** — this lets users select entities they just created without pasting UUIDs. React Context only. |
| `frontend/components/forms/EntitySelect.tsx` | Thin additive form primitive: a `<select>` whose option `value` (UUID) differs from its `label` (human name). Mirrors the styling of the existing `SelectInput`. Needed because the existing `SelectInput` only supports `string[]` (value === label). |
| `frontend/app/dashboard/console/page.tsx` | **Operational Console hub** + Planning Bootstrap. Create Project (auto-selects it as active project), Create WBS Item, Create Location. Session-project switcher, workspace KPI counts, and `SliceNav` (exported, reused by sibling pages). |
| `frontend/app/dashboard/console/activity/page.tsx` | Create Activity Instance (select WBS × Location) and Create Workflow Step (status + planned_weight + progress + ready). Lists session activity instances with deep links to their runtime views. |
| `frontend/app/dashboard/console/execution/page.tsx` | Create Work Order, Assign Work Order → Workflow Step (execution_weight), Submit Daily Report (quantities, manpower/equipment, notes, evidence_metadata JSON), Approve Workflow Step. |

## 2. Files Modified

| File | Change |
| --- | --- |
| `frontend/app/dashboard/layout.tsx` | Wrapped the dashboard subtree with `WorkspaceProvider` (nested inside the existing `ProjectProvider`). |
| `frontend/app/dashboard/activity-instances/[activityInstanceId]/page.tsx` | Enriched the live runtime view: per-step **Approve** action (`POST /runtime/workflow-steps/{id}/approve`) with optimistic disable + automatic `reload()` of the runtime view; per-step display of assigned work orders and their daily-report counts (from the workspace registry); approval-recorded indicator; cross-navigation buttons to the command center and execution console. |
| `frontend/app/dashboard/overview/page.tsx` | Added an "Activity Instances (this session)" card listing project-scoped activities from the workspace registry, each linking to its runtime view — closing the Dashboard → Activity Runtime navigation gap without a backend list endpoint. |

> Note: `frontend/components/layout/Sidebar.tsx` already linked to `/dashboard/console` ("Operational Console"). Stage 16B builds the route that link targets, so the slice is reachable from the global sidebar with no Sidebar edit required.

## 3. Vertical Slice Flows Completed

The full happy path is now executable from the UI:

| # | Step | UI location | Endpoint |
| --- | --- | --- | --- |
| 1 | Login | `/login` | `POST /auth/token` |
| 2 | Project selection / context | Console hub + overview | (client context) |
| 3 | Create Project | `/dashboard/console` | `POST /planning/projects` |
| 4 | Create WBS Item | `/dashboard/console` | `POST /planning/wbs-items` |
| 5 | Create Location | `/dashboard/console` | `POST /planning/locations` |
| 6 | Create Activity Instance | `/dashboard/console/activity` | `POST /planning/activity-instances` |
| 7 | Create Workflow Step | `/dashboard/console/activity` | `POST /planning/workflow-steps` |
| 8 | Create Work Order | `/dashboard/console/execution` | `POST /planning/work-orders` |
| 9 | Assign Work Order | `/dashboard/console/execution` | `POST /runtime/work-orders/{id}/assign` |
| 10 | Submit Daily Report | `/dashboard/console/execution` | `POST /runtime/daily-reports` |
| 11 | Approve Workflow Step | `/dashboard/console/execution` **and** activity runtime page | `POST /runtime/workflow-steps/{id}/approve` |
| 12 | Runtime Dashboard | `/dashboard/overview` | `GET /runtime/projects/{id}/dashboard` |
| 13 | Activity Runtime | `/dashboard/activity-instances/{id}` | `GET /runtime/activity-instances/{id}` |

All status/enum dropdowns are constrained to backend `CHECK`-constraint values (verified against the ORM models): project, activity, workflow-step, work-order, and daily-report statuses. Approval has no backend state precondition (confirmed in `WorkflowGovernanceService.approve_workflow_step`), so approval works from any step status; assignment and daily-report creation only require that the referenced entities exist.

## 4. Runtime Navigation Status

Navigation is fully wired without manual URL editing:

- **Sidebar → Operational Console** (existing link, now functional).
- **Console hub ⇄ Activities ⇄ Execution ⇄ Runtime Dashboard** via the shared `SliceNav` button bar.
- **Dashboard → Activity Runtime**: overview lists session activity instances as links; the existing UUID lookup field remains as a fallback.
- **Activity Runtime → Workflow Step Context → Work Orders → Reports**: the activity runtime page renders each workflow step with its assigned work orders and daily-report counts inline, plus the live Approve action and links back to the command center / execution console.

**Constraint note:** The Phase 1 runtime router exposes only two reads (`GET project dashboard`, `GET activity-instance`). There are no `GET` endpoints for work orders, assignments, or daily reports. "Work Orders" and "Reports" navigation therefore renders from the session workspace registry rather than from server reads. This is a deliberate consequence of the existing backend surface and the "no new endpoints" constraint.

## 5. UUID Migration Status

- The entire Stage 16B surface (workspace registry, console pages, activity runtime page, overview activity list) operates on **UUID strings only**. No numeric IDs, no `parseInt`, no numeric route params.
- All entity selectors use `EntitySelect` with UUID values; all links use UUID path segments (`/dashboard/activity-instances/{uuid}`).
- Local/session state (`WorkspaceContext`, `ProjectContext`) stores UUID strings exclusively.

**Remaining numeric-ID code is fully quarantined to legacy, out-of-slice surfaces** that still talk to the legacy backend and were explicitly out of scope ("do not rebuild pages"): e.g. `/task/[taskId]`, `app/dashboard/daily-reports`, `daily-work-orders`, `workers`, and the legacy `lib/api/*` clients (`reports.ts`, etc.). These are not part of the Phase 1 vertical slice and are not reachable from it.

## 6. Remaining Frontend Gaps

1. **No server-backed listing.** Entity pickers and the runtime "work orders/reports" views are populated from the session registry (localStorage), not from the backend. A page reload on a fresh browser/profile starts with an empty registry until entities are re-created. Requires backend list endpoints to fully resolve.
2. **Runtime reads limited to two views.** Work order, assignment, daily report, and approval detail are not individually fetchable; the UI shows the client-recorded copies.
3. **Legacy pages still present and unmigrated** (daily-reports, daily-work-orders, workers, task detail). They remain on the legacy data/ID model and are isolated from the slice.
4. **No role-based UI gating.** Auth role is decoded and stored, but actions (create/approve) are not yet hidden/disabled by role; the backend still enforces authorization.
5. **i18n not applied to new console views.** New strings are English literals; not yet routed through the `en/fa` message catalog.
6. **No optimistic dashboard refresh.** The overview dashboard reflects backend state on load/retry; it does not auto-refresh after a write performed on another page (manual reload/retry needed).

## 7. Production Blockers

- **No project/entity list endpoints** — the most significant blocker. Operational continuity currently depends on `localStorage`; multi-user, multi-device, and post-reload scenarios need server-side listing/querying.
- **Build verification could not run this session.** The shell/execution environment was unavailable, so `tsc --noEmit` / `next build` / `eslint` were not executed. All changes were verified by source inspection against the Phase 1 API DTOs (`lib/api/phase1/*`), the existing component prop signatures, payload field names, and confirmed CSS classes. A clean `next build` + lint pass must be run once the environment recovers before shipping.
- **Cookie/session hardening** carried over from 16A (token mirrored to a non-`HttpOnly` cookie for middleware; no refresh/expiry handling).
- **No automated end-to-end test** of the happy path yet.

## 8. Recommended Next Stage

**Stage 17 — Runtime Read & Listing Layer (backend + thin UI binding).**

Priorities, in order:

1. Add Phase 1 **list/query endpoints** (`GET /planning/projects`, `GET .../wbs-items?project_id=`, locations, activity-instances, work-orders, daily-reports, assignments, approvals) so the UI no longer depends on the session registry. Then rebind `WorkspaceContext` to a read-through cache over these endpoints.
2. Apply **role-based UI gating** to create/assign/approve actions.
3. Run and gate on **`next build` + ESLint + a Playwright happy-path test** (Login → … → Approve → Dashboard reflects state).
4. Route new console strings through **i18n (en/fa)** and verify RTL.
5. Decommission or migrate the remaining **legacy numeric-ID pages**.

---

## Success Criteria — Status

A real user can execute **Planning → Execution → Progress → Approval → Runtime Visibility** completely from the frontend UI: create project/WBS/location → activity instance → workflow step → work order → assign → daily report → approve → view runtime dashboard and activity runtime. ✅ (Pending the environment-blocked `next build`/lint confirmation noted in §7.)

**Stopping after Stage 16B as instructed.**

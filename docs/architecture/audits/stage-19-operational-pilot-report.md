# Stage 19 — Multi-User Operational Pilot Report

**Stage:** 19 — Multi-User Operational Pilot  
**Type:** Operational validation (not redesign, not new architecture)  
**Scope:** Role boundaries, concurrent operational workflow, concurrency risks, runtime UX audit, query-layer stress review, permission audit, gap identification.

**Pilot personas (mapped to Phase 1 in-memory accounts):**

| Pilot persona | Phase 1 account | Password (demo) |
| --- | --- | --- |
| Project Manager | `admin` | `admin` |
| Site Supervisor | `supervisor` | `supervisor` |
| Engineer | `supervisor` | `supervisor` |
| Worker | `worker` | `worker` |
| Investor / Viewer | `investor` | `investor` |

There is no separate `engineer` role in the JWT model; engineering staff should use the **supervisor** account for the pilot.

---

## 1. Multi-User Workflow Validation

### Vertical slice under concurrent actors

The intended slice remains intact end-to-end:

```
Login → Project → WBS → Location → ActivityInstance → WorkflowStep
     → WorkOrder → Assign → DailyReport → Approve → Dashboard / Runtime views
```

**Validated by architecture review + spot checks:**

| Concern | Finding |
| --- | --- |
| State consistency | Each HTTP request uses one SQLAlchemy session (`get_db`: commit on success, rollback on error). Cross-request consistency depends on PostgreSQL isolation (default READ COMMITTED); no distributed locks. |
| Transaction safety | Single commit per request is correct for Phase 1; multi-step UI flows are multiple transactions (acceptable for pilot, not atomic end-to-end). |
| UI synchronization | **Weak for multi-user.** `WorkspaceContext` (localStorage) is per-browser, not shared. User A’s creates are invisible to User B’s dropdowns until Stage 18-style server list binding is used. Query layer (Stage 17) exists on the backend but is **not yet wired in `frontend/lib/api/phase1/runtime.ts`**. |
| Runtime visibility | Dashboard and activity runtime reads are server-backed (`GET` runtime endpoints). After writes, users must **reload** overview/activity pages; no push/sync. |

**Concurrent pilot narrative (same project):**

1. **Supervisor** creates project structure via Operational Console (`/planning/*`).
2. **Supervisor / admin** creates activities, steps, work orders.
3. **Supervisor** assigns work order to step (`POST .../assign`).
4. **Worker** submits daily report (`POST /runtime/daily-reports`) — now role-enforced.
5. **Supervisor** approves step (`POST .../approve`).
6. **Investor** reads dashboards and lists (`GET /runtime/*`) — no writes.
7. **All roles** see updated progress only after refresh; no live collaboration channel.

**Automated check (role boundaries, no DB required for denials):**

```
worker  → POST /planning/projects     → 403 ✓
investor → POST /planning/projects    → 403 ✓
worker  → POST .../approve            → 403 ✓
investor → POST /runtime/daily-reports → 403 ✓
```

Full multi-user e2e with PostgreSQL was **not executed** in this session (local Postgres unavailable). Pilot teams should run the slice with two browsers and two accounts against a shared dev database.

### Minimal enforcement added (Stage 19)

`backend/phase1/auth/role_policy.py` wires existing `require_roles()` to routers:

| Surface | Policy |
| --- | --- |
| All `/planning/*` POST | `admin`, `supervisor` |
| Runtime GET (lists, dashboards, activity view) | `admin`, `supervisor`, `worker`, `investor` |
| `POST .../assign` | `admin`, `supervisor` |
| `POST /runtime/daily-reports` | `admin`, `supervisor`, `worker` |
| `POST .../approve` | `admin`, `supervisor` |

Validation script: `backend/scripts/stage19_pilot_validation.py` (run with `PYTHONPATH=.` from repo root).

---

## 2. Role-Access Matrix

Legend: **Y** = allowed, **N** = denied (403), **Auth** = any authenticated role, **—** = route does not exist.

### Backend API (after Stage 19 enforcement)

| Action / Route | admin | supervisor | worker | investor |
| --- | --- | --- | --- | --- |
| `POST /auth/token` | Y | Y | Y | Y |
| `POST /planning/*` (all creates) | Y | Y | N | N |
| `GET /runtime/projects` | Y | Y | Y | Y |
| `GET /runtime/projects/{id}/activity-instances` | Y | Y | Y | Y |
| `GET /runtime/activity-instances/{id}/workflow-steps` | Y | Y | Y | Y |
| `GET /runtime/work-orders/{id}/daily-reports` | Y | Y | Y | Y |
| `GET /runtime/projects/{id}/dashboard` | Y | Y | Y | Y |
| `GET /runtime/projects/{id}/dashboard-summary` | Y | Y | Y | Y |
| `GET /runtime/activity-instances/{id}` | Y | Y | Y | Y |
| `POST /runtime/work-orders/{id}/assign` | Y | Y | N | N |
| `POST /runtime/daily-reports` | Y | Y | Y | N |
| `POST /runtime/workflow-steps/{id}/approve` | Y | Y | N | N |

### Frontend (unchanged — audit only)

| Surface | admin | supervisor | worker | investor |
| --- | --- | --- | --- | --- |
| Middleware `/dashboard/*` | Auth cookie only | Same | Same | Same |
| Operational Console (forms) | Visible | Visible | Visible | Visible |
| Console submit → API | Succeeds | Succeeds | **403** (planning/assign/approve) | **403** (all writes) |
| Sidebar legacy ops pages | Visible | Visible | Visible | Visible |
| Role stored (`auth_role`) | Yes | Yes | Yes | Yes |
| Role-based UI hide/disable | **No** | **No** | **No** | **No** |

**Implication:** Backend now separates duties; frontend still presents all actions to all roles. Workers/investors hit 403 on submit — acceptable for pilot if supervisors demo planning, but **not field-ready** without minimal UI gating (Stage 20).

### Recommended pilot ownership

| Persona | Primary actions |
| --- | --- |
| Project Manager / admin | Bootstrap project, override approvals, full visibility |
| Site Supervisor / Engineer | Planning bootstrap, assignments, approvals, dashboard |
| Worker | Daily reports only; read runtime for context |
| Investor | Dashboard + list/query reads only |

---

## 3. Concurrency Findings

| Risk | Severity | Mechanism | Mitigation (pilot) |
| --- | --- | --- | --- |
| **Duplicate work-order assignment** | Medium | DB unique `(work_order_id, workflow_step_id)` — second `POST` fails at persistence (500/integrity error unless handled). | Supervisor coordinates assignments; retry with clear error message (not yet user-friendly). |
| **Duplicate daily reports** | Low–Medium | No unique constraint on `(work_order_id, report_date)`. Same worker can submit twice same day. | Operational discipline; Stage 20 optional uniqueness or idempotency key. |
| **Approval races** | Medium | `approve_workflow_step` has **no** status precondition; multiple supervisors can create **multiple** `Approval` rows; step status set to `APPROVED` repeatedly. | Accept for pilot; add “already approved” guard in governance service later. |
| **Concurrent planning creates** | Low | Unique keys: `projects.code`, `activity_instances (project, code)`, `(project, wbs, location)`. Race → one succeeds, one fails. | Expected; retry with new code. |
| **Stale dashboard reads** | High (UX) | Progress calculated on read; no versioning/ETag. User B may see old progress until refresh. | Manual refresh after approvals; Stage 20 polling or invalidation. |
| **Cross-user UI registry** | High (multi-user) | `WorkspaceContext` is localStorage per browser. | Use Stage 17 list APIs from UI for shared truth. |
| **Session-per-request commits** | Low | Two tabs same user: last commit wins per entity update. | Unlikely in pilot for same entity edits. |

**Deliberately not implemented (per stage scope):** row locks, optimistic concurrency tokens, saga/orchestration, message queues.

---

## 4. Runtime UX Findings (Audit Only — No Redesign)

### Site Supervisor — “Can they run this daily?”

**Partially.** Operational Console + slice nav supports the full bootstrap and execution path in one place. Friction:

- **English-only** console strings; bilingual shell elsewhere.
- **Many forms on three pages** — workable for demo, heavy for daily field use.
- **No server-backed pickers in UI** — still relies on session registry; second supervisor on another machine does not see colleague’s entities in dropdowns.
- **Manual project UUID** on overview if project not created in same browser session.
- Legacy sidebar links (`daily-reports`, `planning`, `daily-work-orders`) still point at **legacy numeric-ID pages**, causing confusion if clicked.

**Verdict:** Viable for controlled pilot with one lead supervisor account; not yet low-friction for multi-supervisor daily ops.

### Worker — “Can they submit reports easily?”

**Partially.** Execution console has a full daily-report form (manpower, equipment, notes, evidence JSON). Friction:

- Worker must navigate **Operational Console → Execution** (not a dedicated “My report” entry).
- Must **select work order from session list** — empty if WO created on another device.
- Backend now allows report POST for worker; **UI does not hide** planning/approve forms (403 on submit is confusing).
- No mobile-specific layout (desktop-first forms).

**Verdict:** Technically possible; UX path is supervisor-oriented, not worker-first.

### Investor — “Can they understand project visibility?”

**Yes, read-only path is clear** once project is selected: overview KPIs + dashboard-summary API (backend). Friction:

- Investor can open console and see create forms (misleading).
- No simplified “portfolio” view across projects without using list endpoint (not in frontend client yet).
- Progress semantics (weighted steps) not explained in UI copy.

**Verdict:** Adequate for investor demo after supervisor sets up data; bind `GET /runtime/projects` for project picker in Stage 20.

### Navigation clarity

| Area | Assessment |
| --- | --- |
| Slice nav (Console → Activity → Execution → Dashboard) | **Good** for vertical-slice demo |
| Sidebar ops group | **Confusing** — mixes Phase 1 console with legacy routes |
| Activity runtime → approve inline | **Good** power feature; risky without role label |
| Auth redirect | Cookie + login works; role not used in middleware |

### Operational overload signals

- Too many fields on bootstrap forms for field pilot.
- Evidence metadata as raw JSON textarea — engineer-friendly, not worker-friendly.
- KPI grids + multiple cards — fine for command center, noisy for worker.

---

## 5. Query-Layer Scalability Findings (Stage 17)

Backend operational query layer is **implemented**; stress validation is **design + code review** (no large dataset load test run).

| Area | Finding |
| --- | --- |
| Pagination | `limit` default 50, max 200; `total` via `count_filtered` — correct for pilot scale. |
| Large projects | `dashboard-summary` loads up to **10,000** activity instances for per-instance progress — will degrade on very large projects. |
| Workflow-step list | Per-step approval/blocker queries → **N+1** pattern per page (acceptable at pilot scale, watch at 100+ steps/page). |
| Filtering | Project name `ILIKE`, activity filters by WBS/location/status — adequate. |
| Sorting | SQL `ORDER BY` on indexed columns — good. |
| Frontend binding | **`frontend/lib/api/phase1/runtime.ts` lacks** `listProjects`, `listActivityInstances`, `listWorkflowSteps`, `listDailyReports`, `getDashboardSummary` — query layer unused in UI for pilot. |
| Responsiveness | Depends on PostgreSQL + network; no CDN/edge cache; no query timeouts configured. |

**Simulated larger dataset (expected behavior):**

- Listing remains stable with pagination.
- Dashboard-summary may slow linearly with activity count.
- Concurrent readers do not block writers (READ COMMITTED).

---

## 6. Permission Boundary Audit

| Check | Result |
| --- | --- |
| Unauthenticated API access | **Blocked** — 401 on `/planning` and `/runtime` (router-level `get_current_active_user`). |
| Unauthenticated UI `/dashboard` | **Redirect** to `/login` if `auth_token` cookie missing. |
| JWT tampering / expiry | **Rejected** — `TokenError` → 401 (HS256 + exp). |
| Role escalation via JWT | Role embedded at login; changing claim without re-login fails signature check. Client-side role in localStorage is **not trusted** (correct). |
| Worker/investor planning writes | **Blocked** — 403 after Stage 19. |
| Investor writes | **Blocked** — 403 on all runtime POSTs. |
| Project isolation | **Not enforced** — any authenticated user can pass any `project_id` UUID to GET/POST; **no project membership model**. Critical pilot limitation for multi-tenant production. |
| Approval authority | Any supervisor/admin can approve any step; `approved_by` optional and not tied to JWT `sub`. |
| Cookie security | `auth_token` readable by JS (non-HttpOnly) — XSS risk remains. |

---

## 7. Operational Gaps (Identify Only — Not Implemented)

### Missing runtime / list UX (frontend)

- Server-backed project picker on overview (use `GET /runtime/projects`).
- Server-backed entity selectors in console (activities, WOs, steps).
- Work-order list at project scope (`GET` list for work orders not implemented in Stage 17).
- Dedicated worker “submit report” entry point.
- Role-aware visibility (hide console for investor/worker).

### Missing collaboration / audit

- No audit trail (who created/approved/report).
- No notifications (approval requested, report submitted).
- No comments/@mentions on steps or reports.
- No real-time or polling refresh.

### Missing governance

- No project-level ACL / membership.
- No approval workflow states (only direct approve).
- No “reject report” or inspection workflow in UI.
- Engineer persona not first-class (mapped to supervisor).

### Missing operational workflows

- Rework / inspection pending flows exist in enums but not in pilot UI path.
- BOQ linkage not in vertical slice UI.
- Blocker create/resolve not exposed in UI (only visible on step list API).

### Data / ops

- In-memory user registry (restarts lose nothing, but not real IAM).
- No refresh tokens / session revocation.
- Legacy pages still in navigation.

---

## 8. Production Blockers

1. **No project isolation** — multi-project pilot is OK only if all users are trusted on one project; not safe for multi-tenant production.
2. **Frontend role/UI mismatch** — 403 errors instead of guided read-only or worker-specific surfaces.
3. **Query layer not bound in frontend** — multi-user operational visibility still breaks across browsers.
4. **In-memory auth users** — not enterprise IAM (LDAP/OIDC), no password policy, default demo passwords.
5. **JWT in non-HttpOnly cookie** — security hardening required.
6. **No automated multi-user e2e test suite** in CI.
7. **PostgreSQL required** — pilot environment must be shared and migrated; no embedded DB for production.
8. **Duplicate approvals/reports** — governance gaps for concurrent supervisors.
9. **dashboard-summary scale** — unbounded activity iteration for large projects.

---

## 9. Recommended Stage 20 — Production Pilot Hardening

Prioritized, minimal-scope follow-up (still no architecture rebuild):

1. **Frontend operational binding (Stage 18 carryover)** — Wire Stage 17 query APIs; replace `WorkspaceContext` pickers with server lists; project selector on overview.
2. **Minimal role-aware UI** — Hide/disable console sections by `getAuthRole()` (investor: overview + lists only; worker: execution report form only).
3. **Project scoping policy** — Minimal `project_membership` or claim-based access in JWT (even static config for pilot).
4. **Governance guards** — Idempotent approve; optional unique daily report per WO+date; friendlier duplicate-assign error mapping to 409.
5. **Pilot playbook + shared Postgres** — Document two-browser test script; add CI smoke with TestClient + role matrix (extend `stage19_pilot_validation.py`).
6. **Security baseline** — HttpOnly cookie option, rotate `BETAVANX_AUTH_SECRET`, remove demo passwords from production builds.

---

## Success Criteria — Assessment

| Criterion | Status |
| --- | --- |
| Multi-user operational viability | **Partial** — backend roles enforced; shared DB + UI binding required for true concurrency |
| Role separation | **Backend yes** / **Frontend no** |
| Runtime consistency | **Acceptable** per-request; stale reads + local registry remain |
| Operational visibility | **Good** for reads when DB shared; **Poor** cross-browser without list UI |
| Usable daily workflows | **Demo-ready** for single lead supervisor; **not field-ready** for worker/investor without Stage 20 |
| No architectural collapse | **Pass** — changes limited to `role_policy.py` + router dependencies |

**Stopping after Stage 19 as instructed.**

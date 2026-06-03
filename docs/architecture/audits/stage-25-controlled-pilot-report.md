# Stage 25 — Controlled Real-World Pilot Report

**Stage:** 25 — Controlled Operational Pilot  
**Type:** Operational reality validation (no redesign, no new product domains)  
**Prerequisites:** Stages 20–24 (frontend binding, persistence, hardening, deployment, scale/IAM)

---

## Executive Summary

Stage 25 validates BetavanX under **realistic human operational conditions**: multi-role workflows, deployment survivability, lightweight metrics, and a minimal feedback channel. This is an **audit-first** stage — findings are documented; UI and architecture were not redesigned.

| Area | Assessment |
| --- | --- |
| End-to-end operational flow | **Runnable** when PostgreSQL + seed users are up; console covers Planning → Execution → Report → Approve → Visibility |
| Human usability | **Adequate for pilot** with documented friction (project selection, console discoverability, mobile/desktop gap) |
| Runtime reliability | **Strong** with Stage 22 optimistic locking + polling; **degraded** without DB (auth/login 500 on persisted IAM) |
| Pilot metrics | **Instrumented** via `stage25_controlled_pilot_simulation.py` + `stage25_pilot_metrics.py` |
| Failure modes | Catalogued below (stale UI, duplicate nav targets, offline auth) |
| Production readiness | **Pilot-ready** in Docker; **not contractor-production** until password/OIDC, field mobile, and human pilot notes close gaps |
| Feedback layer | **Implemented** — `POST /pilot/feedback`, Overview form, JSONL store |

**Local verification (2026-06-03):** With PostgreSQL offline, `/health` → 503; simulation recorded role-login attempts only (~4.2s each, HTTP 500 on token — persisted IAM requires DB). Full timed vertical slice and metrics run in **Stage 25 CI** (`pilot-postgres` job) and via `docker compose up`.

---

## 1. Operational Workflow Findings

### Validated flow (design intent)

```mermaid
flowchart TD
  P[Planning: project → WBS → location → activity → step → WO]
  E[Execution: assign WO to step]
  R[Daily report: worker submit]
  A[Approval: supervisor approve step]
  V[Runtime visibility: overview KPIs + activity detail]
  D[Dashboard review: investor read-only / admin refresh]
  P --> E --> R --> A --> V --> D
```

| Step | Surface | Roles | Friction / notes |
| --- | --- | --- | --- |
| Planning chain | `/dashboard/console` (+ activity sub-routes) | admin, supervisor | **High step count** — six creates before field work; no wizard. Acceptable for pilot admins; slow for first-time supervisors. |
| Execution / assign | `/dashboard/console/execution` | admin, supervisor | Work-order list now server-backed (Stage 21). Assign still requires knowing workflow step ID via selects — **cognitive load** if many activities. |
| Daily report | Console execution forms | worker, supervisor | Tied to work order + optimistic `expected_work_order_updated_at` — **409 on stale WO** if user keeps form open after assign (Stage 22). |
| Approval | Activity runtime + console activity | supervisor, admin | Role-gated `canApproveSteps()` (Stage 20). Stale step token → **409**; user must refresh polling (30–45s) or reload. |
| Runtime visibility | Overview, activity instance page | all readers | Overview polls every 30s; activity 45s — **intentional** freshness vs. load. |
| Dashboard review | Overview KPIs + summary API | investor read-only | Investor auto-granted on project create (policy); summary readable if membership/grant OK. |

### Bottlenecks (audit only — no redesign)

1. **Planning-before-execution ordering** — No shortcut to “report on today’s WO” without prior planning entities.
2. **Duplicate nav targets** — `nav_daily_reports` and `nav_work_orders` both route to `/dashboard/console/execution` (discoverability confusion).
3. **Project context** — Overview blocks until project selected; correct for scoping but **onboarding friction** for new pilots.
4. **Legacy redirects** — Old `/dashboard/planning` paths redirect to console; bookmarks may confuse veteran testers.

### Redundant steps observed

- Creating both **activity instance** and **workflow step** before **work order** — domain-accurate but heavy for a single field task pilot.
- **WorkspaceContext** fallback on execution page when server list empty — same-browser session only; redundant with server list when DB up.

---

## 2. Human Usability Findings

| Dimension | Finding | Severity |
| --- | --- | --- |
| Onboarding | Login uses Phase 1 JWT (`/auth/token`); pilot passwords documented in playbook — **rotate before external pilot** | Operational risk |
| Navigation | Role-filtered sidebar (overview + console for operators); investors see overview only | OK |
| Workflow discoverability | Console hub vs. activity deep-link — supervisors must learn two areas | UX risk |
| Mobile | Desktop-first layout; console forms not audited as field-phone optimized | **Gap for site workers** |
| Worker usability | Daily report on execution page; depends on prior assign + membership | OK with training |
| Supervisor workload | Many planning forms + approval on activity page — **high context switching** | UX risk |
| Investor readability | KPI cards + read-only messaging on overview | OK |
| i18n / RTL | Persian/English provider present; operational console copy mostly English | Minor |
| Runtime overload | Batch workflow-steps (Stage 24) reduced N+1; overview still multi-card | Improved |

### Operational misunderstandings (pilot training topics)

- **403 on runtime** — Usually wrong project or role; not a “broken login.”
- **409 on submit/approve** — Concurrent edit; refresh and retry with new `updated_at`.
- **Empty work-order list** — Often no assign yet or wrong project selected.

### Pain points to capture during live pilot

Use Overview **Pilot feedback** or `data/pilot_feedback.jsonl` for qualitative notes. Automated probe writes one JSONL line during simulation when DB is up.

---

## 3. Runtime Reliability Findings

| Check | Result | Evidence |
| --- | --- | --- |
| Long-running sessions | JWT TTL from env (Stage 23 prod example: shorter TTL) | Config templates |
| Repeated report submissions | Optimistic guard on work order | Stage 22 `expected_work_order_updated_at` |
| Project switching | `ProjectContext` + authorized project list | Stage 20–21 |
| Runtime refresh | `useRuntimePolling` 30s/45s | Stage 22 |
| Role switching | New login required per user (no in-app role switch) | By design |
| Membership enforcement | `ProjectAccessService` 403 on cross-project | stage21/22 postgres scripts |
| Deployment uptime | Compose healthchecks on PG + `/health` | Stage 23 |
| Restart recovery | entrypoint: schema + Alembic + seed | `docker-entrypoint.sh` |
| Auth without DB | **Unstable** — token endpoint hits persisted users → 500 when PG down | Local simulation 2026-06-03 |

### Operational instability

- **Offline / 503 health:** App degrades; login not meaningful without Postgres after Stage 24 IAM persistence.
- **In-process load tests** inflate latency (Stage 24 note) — do not use as field SLA.

---

## 4. Pilot Metrics

### Instrumentation added (Stage 25)

| Artifact | Purpose |
| --- | --- |
| `backend/scripts/stage25_controlled_pilot_simulation.py` | Timed API vertical slice + JSON metrics |
| `backend/scripts/stage25_pilot_metrics.py` | Human-readable summary of metrics file |
| `backend/scripts/stage25_deployment_validation.py` | Compose artifacts + Stage 23 smoke + simulation |
| `logger betavanx.pilot_metrics` | `pilot_metric feedback_submitted` on feedback POST |
| `docs/pilot/controlled-pilot-playbook.md` | Operator runbook |

### Sample metrics (PostgreSQL offline — local run)

| Metric | Value | Note |
| --- | --- | --- |
| `database_available` | false | `/health` → 503 |
| `login_*` (API) | ~4200 ms, HTTP 500 | IAM/DB unavailable |
| Full vertical slice | not run | Requires CI Postgres or `docker compose` |

### Expected metrics (with Postgres — CI / Compose)

When `database_available` is true, simulation records ms for:

- `create_project`, `create_wbs`, `create_location`, `create_activity`, `create_workflow_step`, `create_work_order`, `assign_work_order`, `submit_daily_report`, `approve_workflow_step`, `dashboard_summary`, `workflow_steps_batch`, `pilot_feedback`, `investor_dashboard`

**Targets for human pilot (guidance, not SLAs):**

| Metric | Pilot target (guidance) |
| --- | --- |
| Time to create workflow (planning + assign) | &lt; 5 min trained / &lt; 15 min first-time |
| Time to submit report | &lt; 2 min |
| Approval latency | &lt; 1 business day (process); API &lt; 2s on LAN |
| Dashboard summary (API) | &lt; 500 ms on Compose LAN |
| User error frequency | Track 4xx/409 per session in feedback |
| Conflict frequency | 409 count from simulation `conflicts` + pilot notes |

Run: `STAGE25_METRICS_PATH=data/stage25_metrics.json python backend/scripts/stage25_controlled_pilot_simulation.py`

---

## 5. Failure-Mode Analysis

| Pattern | Cause | Mitigation (existing) |
| --- | --- | --- |
| Stale dashboards | Polling interval + concurrent writes | Manual refresh; 409 on stale mutate |
| Accidental duplicate actions | Double-submit approve/report | Optimistic locking → 409 |
| Operational confusion | Many entities before WO | Playbook + training |
| Unauthorized attempts | Role/membership | 403 + audit logs |
| Slow runtime flows | Cold DB, in-process test client | External load test URL (Stage 24) |
| Broken navigation | Duplicate hrefs to execution | Document; Stage 26 may split routes |
| Missing visibility | No project selected | Overview gate |
| Auth 500 without DB | Persisted IAM | Require healthy Postgres in pilot |
| Default pilot passwords | Seed users | Env + rotation (Stage 23 prod rules) |

---

## 6. Production Blockers

### Critical blockers (real contractor / site usage)

| Blocker | Why |
| --- | --- |
| Default pilot credentials | Unacceptable on open networks |
| Mobile / field UX not validated | Workers on phones need dedicated audit |
| No OIDC / enterprise IAM | Contractor IT standards |
| Human pilot sign-off missing | This report is **pre-pilot + automated**; qualitative gaps need JSONL feedback |

### Operational risks

| Risk | Class |
| --- | --- |
| Single API replica in Compose | Scaling |
| Investor grant policy vs. membership rows | Multi-project visibility |
| 409 without user-facing copy | Support burden |
| Backup restore not exercised in this run | Ops |

### UX risks

| Risk | Class |
| --- | --- |
| Console vs. overview split | Discoverability |
| Duplicate nav entries | Navigation |
| Long planning chain | Adoption |

### Scaling risks

| Risk | Class |
| --- | --- |
| Horizontal API scaling untested under pilot load | Infrastructure |
| No read replica / cache at 10k+ steps | Performance (Stage 24) |

---

## 7. Operational Adoption Risks

1. **Organizational resistance** — Perceived complexity (WBS → activity → step → WO) vs. paper daily logs.
2. **Supervisor as bottleneck** — Approvals and planning concentrated on one role.
3. **Worker training** — 409/403 messages require plain-language runbook (playbook §).
4. **Investor trust** — KPIs depend on timely approvals and reports; stale data if process lags.
5. **Multi-project switching** — Admins must discipline project selector per site visit.

---

## 8. Stage 25 Deliverables Implemented

| Deliverable | Location |
| --- | --- |
| Pilot feedback API | `POST /pilot/feedback` — `backend/phase1/routers/pilot_router.py` |
| JSONL store | `backend/phase1/pilot/feedback_store.py` (`PILOT_FEEDBACK_PATH`) |
| Overview feedback UI | `frontend/components/pilot/PilotFeedbackForm.tsx` |
| Playbook | `docs/pilot/controlled-pilot-playbook.md` |
| Scripts | `backend/scripts/stage25_*.py` |
| CI | `.github/workflows/stage25-ci.yml` |

---

## 9. Deployment Validation

| Check | Status |
| --- | --- |
| Docker Compose stack | Present (Stage 23) — `docker-compose.yml`, Dockerfiles, entrypoint |
| PostgreSQL persistence | Required for IAM + membership |
| Alembic migrations | `20260603_0001`–`0003` chain (Stages 22–24) |
| Restart recovery | entrypoint bootstrap documented |
| Auth/session | JWT bearer; role must match DB (Stage 24) |
| Backup/restore | `docs/operations/backup-recovery.md` — **operator must run restore drill** |
| Automated smoke | `stage25_deployment_validation.py` wraps Stage 23 + Stage 25 simulation |

**Operator command:**

```bash
cp .env.docker.example .env.docker
docker compose --env-file .env.docker up --build
PYTHONPATH=. python backend/scripts/stage25_deployment_validation.py
```

---

## 10. Recommended Stage 26

Prioritize from **pilot feedback JSONL** and human sessions — not speculative features.

1. **Close critical blockers** — Force non-default secrets; disable seed passwords in production; document OIDC path.
2. **Field mobile pass** — Touch targets, execution/report path on small screens; optional PWA smoke.
3. **Navigation clarity** — Separate daily-report vs. work-order nav targets (minimal route split, not redesign).
4. **409/403 UX copy** — Inline messages on console forms (small copy change).
5. **External load CI nightly** — `LOAD_TEST_BASE_URL` against Compose; archive p95.
6. **Restore drill** — Execute backup doc once; record RTO in ops doc.
7. **Aggregated dashboard payload** (optional) — Only if batch + summary still insufficient after pilot metrics.

---

## 11. Success Criteria (Stage 25)

| Criterion | Met? |
| --- | --- |
| Real operational usability (documented flows + playbook) | Yes — pending live human sign-off |
| Stable multi-user workflows (automated role matrix + PG E2E in CI) | Yes — when Postgres up |
| Survivable runtime behavior (locking, polling, deploy stack) | Yes |
| Understandable operational flows (with training caveats) | Partial |
| Deployable contractor-facing runtime | Pilot-ready in Docker; production blockers listed |

---

## Verification Commands

```bash
# Offline smoke
set PYTHONPATH=.
set SKIP_STARTUP_VALIDATION=true
python backend/scripts/stage25_deployment_validation.py

# With Postgres
set DATABASE_URL=postgresql://betavanx_app:PASSWORD@localhost:5432/betavanx_dev
set SKIP_STARTUP_VALIDATION=false
python backend/scripts/phase1_init_schema.py
alembic -c backend/alembic.ini upgrade head
python backend/scripts/seed_platform_users.py
set STAGE25_METRICS_PATH=data/stage25_metrics.json
python backend/scripts/stage25_controlled_pilot_simulation.py
python backend/scripts/stage25_pilot_metrics.py

# Frontend build
cd frontend && npm run build
```

---

**Stage 25 complete.** Do not proceed to Stage 26 implementation within this deliverable scope.

# Stage 24 — Operational Scale Report

**Stage:** 24 — Persisted IAM, Batch Queries & External Load Test  
**Type:** Production-scale readiness (no redesign, no new Phase 1 entities)  
**Prerequisite:** Stage 23 Deployment & Operational Hardening complete

---

## Executive Summary

Stage 24 prepares BetavanX Phase 1 for **production-scale operational usage** by persisting platform IAM in PostgreSQL, adding a **batch workflow-steps dashboard API** (replacing frontend N+1 reads), introducing verification and load-test tooling, and validating the Alembic migration chain through `20260603_0003`.

| Area | Status |
| --- | --- |
| Persisted IAM (`platform_users`) | Implemented + migration |
| Project membership persistence | Already persisted (Stage 22+); indexes verified |
| Batch dashboard queries | Implemented (API + frontend hook) |
| External / in-process load test | Implemented (`stage24_load_test.py`) |
| Alembic repeatability | Validated via `stage24_alembic_validation.py` |
| CI | `.github/workflows/stage24-ci.yml` |
| Multi-user vertical slice | Scripts + Postgres E2E |

**Verification note:** In-process load tests inflate latency (each thread constructs a new `TestClient`/`create_app()`). For realistic 50–200 user measurements, run against Docker with `LOAD_TEST_BASE_URL=http://localhost:8000`.

---

## 1. Persisted IAM Verification

### Before Stage 24

Pilot users lived in an in-memory `_USERS` map inside `backend/phase1/auth/auth.py`. Project **memberships** were already stored in `project_memberships`.

### After Stage 24

| Component | Path | Role |
| --- | --- | --- |
| Model | `backend/phase1/models/platform_user.py` | Table `platform_users` |
| Repository | `backend/phase1/repositories/platform_user_repository.py` | CRUD + role listing |
| Service | `backend/phase1/auth/user_service.py` | Auth, seed, `list_usernames_by_roles` |
| Token endpoint | `backend/phase1/auth/auth.py` | `ensure_seed_users(PILOT_SEED_USERS)` on login |
| Current user | `backend/phase1/auth/dependencies.py` | JWT `role` must match DB role |
| Project grants | `backend/phase1/auth/project_access.py` | Role-based username lists from DB |
| Seed script | `backend/scripts/seed_platform_users.py` | Idempotent pilot users |
| Docker | `backend/docker-entrypoint.sh` | `RUN_SEED_PLATFORM_USERS=true` (default) |

### Enforcement matrix (automated)

`stage24_iam_verification.py` and `stage19_pilot_validation.py` confirm:

- All four roles obtain tokens with matching `sub` and `role` claims.
- Tampered JWT role (`admin` sub + `worker` role) → **401**.
- Worker cannot POST `/planning/projects` → **403**.
- Runtime reads require `require_runtime_reader` + `ProjectAccessService.ensure_project_access`.

### Database indexes

| Table | Indexes |
| --- | --- |
| `platform_users` | PK `username`, `idx_platform_users_role` (Alembic `20260603_0003`) |
| `project_memberships` | `idx_project_memberships_username`, `idx_project_memberships_project_id` (Alembic `20260603_0001`) |

### Postgres checks (when `DATABASE_URL` is live)

- `SELECT COUNT(*) FROM platform_users` ≥ 4 after seed/login.
- Required indexes present on `platform_users` and `project_memberships`.

---

## 2. Batch Query Implementation and Validation

### Problem

`useProjectWorkflowStepOptions` previously called `listActivityInstances` then **one `listWorkflowSteps` per activity** (N+1), causing client and server churn on large projects.

### Solution

**Endpoint:** `GET /runtime/projects/{project_id}/workflow-steps-batch`

| Parameter | Default | Max |
| --- | --- | --- |
| `limit` | 50 | 500 |
| `offset` | 0 | (Stage 17 offset dependency) |
| `status` | optional filter | — |

**Backend optimizations** (`runtime_query_service.py`):

- Single JOIN query for project workflow steps + activity metadata.
- Batched `list_for_workflow_step_ids` for approvals and blockers.
- `count_by_project_id` for totals (also used in `get_project_runtime_summary`).

**Frontend:**

- `listProjectWorkflowStepsBatch` in `frontend/lib/api/phase1/runtime.ts`
- `useProjectWorkflowStepOptions` uses one batch call (`limit: 500`)

### Validation

- `stage24_postgres_validation.py`: pagination shape, worker **403** on unrelated project batch, admin **200**.
- No new runtime **calculation** logic; read-only aggregation only.

---

## 3. Load Test Results

### Tooling

`backend/scripts/stage24_load_test.py`

| Env var | Default | Purpose |
| --- | --- | --- |
| `LOAD_TEST_USERS` | 50 | Concurrent virtual users (target 50–200) |
| `LOAD_TEST_ITERATIONS` | 5 | Requests per user |
| `LOAD_TEST_BASE_URL` | (empty) | External API URL (Docker / staging) |
| `LOAD_TEST_MAX_WORKERS` | 32 | Thread pool cap |

### Traffic profile

- Rotating roles: admin, supervisor, worker, investor.
- Reads: `/runtime/projects`, `/health/live`, project `dashboard-summary`, `workflow-steps-batch`.
- Writes (admin/supervisor/worker subset): project create, work order create, daily report submit with optimistic concurrency field.

### Expected findings (pilot in-process)

| Metric | Typical in-process | Production target |
| --- | --- | --- |
| p50 latency | Low (single machine) | < 200 ms reads |
| p95 latency | Often elevated | < 1 s reads at 100 users |
| Worker failures | 0 | 0 |
| HTTP/logic errors | Low with empty DB | Monitor 409/422 conflict rate |

**Bottleneck (documented):** per-thread `TestClient(create_app())` — not representative of uvicorn worker pool + shared connection pool. Stage 25 should use `LOAD_TEST_BASE_URL` against horizontally scaled API + tuned `DB_POOL_SIZE`.

### Operator command (external)

```bash
docker compose --env-file .env.docker up -d
export LOAD_TEST_BASE_URL=http://localhost:8000
export LOAD_TEST_USERS=100
export LOAD_TEST_ITERATIONS=10
PYTHONPATH=. python backend/scripts/stage24_load_test.py
```

---

## 4. Alembic Migration Validation

### Chain

```
20260603_0001  project_memberships + indexes
    ↓
20260603_0002  work_orders list composite index
    ↓
20260603_0003  platform_users + role index
```

### Script

`stage24_alembic_validation.py`:

1. `alembic upgrade head`
2. `alembic downgrade -1` (rolls back `platform_users`)
3. `alembic upgrade head` (repeatable)
4. Asserts `platform_users`, `project_memberships`, `alembic_version == 20260603_0003`

Greenfield installs: `phase1_init_schema.py` + `alembic upgrade head` (Docker entrypoint).

---

## 5. Multi-User Vertical Slice Audit

| Check | Script | Result |
| --- | --- | --- |
| Role matrix (403 paths) | `stage19_pilot_validation.py` | Pass (no DB) |
| Extended pilot | `stage21_pilot_validation.py` | Pass |
| IAM + JWT binding | `stage24_iam_verification.py` | Pass |
| Postgres E2E + scoping | `stage22_postgres_validation.py`, `stage24_postgres_validation.py` | Pass with Postgres |
| Batch + dashboard | `stage24_postgres_validation.py` | Pass |
| Performance indexes | `stage23_postgres_performance_audit.py` | Pass with Postgres |
| Load simulation | `stage24_load_test.py` | Pass (CI: 50 users × 3 iter) |
| Integrity / audit | Existing mutation audit middleware (Stage 20+) | Unchanged |

**Concurrency:** Daily reports and assignments continue to use `expected_*_updated_at` optimistic guards (Stage 22).

---

## 6. Remaining Operational Gaps

| Gap | Impact | Notes |
| --- | --- | --- |
| In-process load test | Misleading p95 | Use external URL for Stage 25 benchmarks |
| No dedicated k6/Locust suite | Ops tooling | Script is sufficient for Phase 1 pilot |
| Investor project auto-grant | Product policy | Investors see projects via role-based grant list, not membership rows for every project |
| Horizontal API scaling | High concurrency | Single uvicorn process in Docker Compose |
| Read replica / caching | Dashboard at 10k+ steps | Batch endpoint reduces round-trips; caching deferred |
| Password rotation / OIDC | Enterprise IAM | Out of Phase 1 scope |

---

## 7. Recommendations for Stage 25

1. **External load harness** — Run `stage24_load_test.py` with `LOAD_TEST_BASE_URL` in CI nightly against Compose; archive p50/p95 and error rates.
2. **Connection pool tuning** — Document `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` vs. `LOAD_TEST_USERS`; add pool exhaustion metrics.
3. **API horizontal scale** — Multiple uvicorn workers or replicas behind a reverse proxy; validate session-less JWT auth under load.
4. **Batch KPI endpoint** — Optional aggregated dashboard payload (single round-trip) if batch steps + summary still insufficient.
5. **IAM hardening** — Disable default pilot passwords in production via env; require `BETAVANX_AUTH_SECRET` rotation (Stage 23 validation already enforces in prod/staging).
6. **Stale-read monitoring** — Compare dashboard-summary totals vs. batch `total` under concurrent writes; alert on divergence.

---

## Artifacts Added / Updated (Stage 24)

| Artifact |
| --- |
| `backend/phase1/models/platform_user.py` |
| `backend/phase1/repositories/platform_user_repository.py` |
| `backend/phase1/auth/user_service.py` |
| `backend/alembic/versions/20260603_0003_platform_users.py` |
| `backend/scripts/seed_platform_users.py` |
| `backend/scripts/stage24_*.py` |
| `GET .../workflow-steps-batch` + `runtime_query_service` batch paths |
| `frontend/lib/api/phase1/runtime.ts`, `usePhase1Lists.ts` |
| `.github/workflows/stage24-ci.yml` |

---

## Verification Commands

```bash
# No Postgres (degraded: deployment verification only; IAM/login need Postgres)
set PYTHONPATH=.
set SKIP_STARTUP_VALIDATION=true
python backend/scripts/stage24_runtime_verification.py

# With Postgres / CI
set RUN_POSTGRES_VALIDATION=true
python backend/scripts/stage24_runtime_verification.py

# Frontend
cd frontend && npm run build
```

---

**Stage 24 complete.** Do not proceed to Stage 25 implementation within this deliverable scope.

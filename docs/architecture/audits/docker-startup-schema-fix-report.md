# Docker Startup Schema Fix Report

**Type:** Startup orchestration fix (no business logic change)  
**Issue:** `relation "project_memberships" already exists` on backend container start

---

## Root Cause

Docker entrypoint ran **two** schema paths on every boot:

```text
1. python backend/scripts/phase1_init_schema.py   → Base.metadata.create_all()
2. alembic upgrade head                           → 20260603_0001 creates project_memberships again
```

| Source | What it creates |
| --- | --- |
| `phase1_init_schema.py` | All Phase 1 ORM tables (including `project_memberships`, `platform_users`) |
| Alembic `20260603_0001` | `project_memberships` table + indexes |
| Alembic `20260603_0003` | `platform_users` (also on ORM metadata → `create_all` already created it) |

`create_all()` is idempotent (`checkfirst=True`). **Alembic `op.create_table()` is not** — second run fails with **already exists**.

PostgreSQL itself was healthy; failure was **duplicate DDL orchestration**, not database corruption.

---

## Fixes Applied

### 1. `backend/docker-entrypoint.sh`

- **Default `RUN_SCHEMA_BOOTSTRAP=false`** — does not run `phase1_init_schema.py` in Docker.
- **Default `RUN_ALEMBIC_UPGRADE=true`** — `alembic upgrade head` is the single automatic schema path.
- If `RUN_SCHEMA_BOOTSTRAP=true` is set explicitly, a **deprecation warning** is logged (escape hatch for local debugging only).

### 2. `docker-compose.yml` / `.env.docker.example`

- `RUN_SCHEMA_BOOTSTRAP` default changed from `true` → **`false`**.

### 3. Alembic chain (greenfield + idempotent)

| Revision | Purpose |
| --- | --- |
| `20260603_0000` | **New** — `create_all(checkfirst=True)` for full Phase 1 core schema |
| `20260603_0001` | `project_memberships` — **`if_not_exists=True`** |
| `20260603_0002` | Work orders index — **`if_not_exists=True`** |
| `20260603_0003` | `platform_users` — **`if_not_exists=True`** |

- `20260603_0001` now revises `20260603_0000` (was root-only).
- Existing databases already stamped at `20260603_0003` **do not re-run** `0000`; no migration rewrite required for them.

### 4. `backend/scripts/phase1_init_schema.py`

- **Retained in repo** for manual bootstrap and CI workflows.
- Docstring updated: **not** used by Docker entrypoint.

---

## Clean Startup Sequence (Docker)

```text
PostgreSQL (healthy)
    ↓
Wait for DB (entrypoint Python probe)
    ↓
alembic upgrade head          ← sole schema source
    ↓
seed_platform_users.py        ← pilot IAM rows (optional RUN_SEED_PLATFORM_USERS)
    ↓
uvicorn backend.phase1.app:app
    ↓
GET /health → 200 (DB connected)
```

**Removed from default path:** `phase1_init_schema.py`

---

## Implementation notes

- **`if_not_exists=True`** on `op.create_table()` must be the **last** keyword argument (after all columns/constraints). Placing it before `sa.Column(...)` caused a Python `SyntaxError` and blocked Alembic in Docker.
- **Local `.env.docker`:** If copied from an older template, set `RUN_SCHEMA_BOOTSTRAP=false` so compose does not override the compose-file default.
- **`python-multipart`** was added to `requirements.txt` so the entrypoint seed step and FastAPI form login can load in the container image (unrelated to duplicate DDL, required for `/health` verification).

---

## Verification

### Automated (requires PostgreSQL)

```bash
PYTHONPATH=. alembic -c backend/alembic.ini upgrade head
PYTHONPATH=. alembic -c backend/alembic.ini upgrade head   # must succeed twice
PYTHONPATH=. python backend/scripts/docker_startup_schema_verification.py
```

### Docker Compose

```bash
docker compose --env-file .env.docker up --build
```

| Check | Expected |
| --- | --- |
| Backend logs | No `project_memberships already exists` |
| Second container restart | `alembic upgrade head` no-op at head |
| `GET http://localhost:8000/health` | 200, database connected |
| `alembic_version` | `20260603_0003` |

### Stale volume recovery

If a volume was created with the **old** double-bootstrap and is in a bad state:

```bash
docker compose down -v    # drops betavanx_pgdata
docker compose --env-file .env.docker up --build
```

Or keep data and ensure `alembic_version` is at head; repeat `upgrade head` with new idempotent revisions.

---

## Duplicate Table Creation — Before vs After

| Scenario | Before | After |
| --- | --- | --- |
| Fresh volume, compose up | create_all + 0001 → **error** | 0000→0003, **ok** |
| Restart backend | create_all + 0001 → **error** | upgrade head no-op, **ok** |
| Manual `RUN_SCHEMA_BOOTSTRAP=true` | Duplicate risk remains | Warn + only if explicitly enabled |

---

## Remaining Gaps

1. **CI workflows** still run `phase1_init_schema.py` then Alembic — acceptable (idempotent migrations now); optional CI simplification later.
2. **`docs/operations/backup-recovery.md`** still mentions both paths — update when ops docs are next edited.
3. **Existing broken volumes** may need `docker compose down -v` once if `alembic_version` is missing but tables exist.
4. **`0000` downgrade** is no-op by design — full schema drop not automated (destructive).

---

## Files Changed

| File | Change |
| --- | --- |
| `backend/docker-entrypoint.sh` | Alembic-only default; bootstrap opt-in |
| `docker-compose.yml` | `RUN_SCHEMA_BOOTSTRAP:-false` |
| `.env.docker.example` | Document Alembic-only default |
| `backend/alembic/versions/20260603_0000_phase1_core_schema.py` | New |
| `backend/alembic/versions/20260603_0001_*.py` | `if_not_exists`, revises 0000 |
| `backend/alembic/versions/20260603_0002_*.py` | `if_not_exists` on index |
| `backend/alembic/versions/20260603_0003_*.py` | `if_not_exists` |
| `backend/scripts/phase1_init_schema.py` | Docstring only |
| `backend/scripts/docker_startup_schema_verification.py` | New verification |
| `backend/scripts/stage24_alembic_validation.py` | Repeat upgrade head check |
| `requirements.txt` | `python-multipart` for Docker seed/API startup |

### Verified (2026-06-04, local Docker)

| Step | Result |
| --- | --- |
| Fresh volume + `RUN_SCHEMA_BOOTSTRAP=false` | Alembic only; no `phase1_init_schema` in logs |
| `GET /health` | `200`, `database: connected` |
| Backend restart ×2 | No `project_memberships already exists`; `alembic_version = 20260603_0003` |

---

**Docker startup schema fix complete.**

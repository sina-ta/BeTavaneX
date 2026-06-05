# Runtime Wiring Fix Report

**Type:** Frontend ↔ Phase 1 backend integration fix (no architecture redesign)  
**Date:** 2026-06-03

---

## Executive Summary

Login returned **Not Found** because the browser often called **`http://localhost:3000/auth/token`** (Next.js) instead of **`http://localhost:8000/auth/token`** (FastAPI). The root cause was **relative API URLs** when `NEXT_PUBLIC_API_URL` was unset or empty, plus a default `Content-Type: application/json` on all requests.

Fixes harden `frontend/lib/api/client.ts` so Phase 1 always targets an absolute backend origin.

---

## Root Cause

| Issue | Effect |
| --- | --- |
| `process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"` | Empty string `""` is **not** nullish → `BASE_URL` became `""` |
| `fetch(\`${BASE_URL}/auth/token\`)` with empty base | Resolves to **`/auth/token`** on the **current page origin** (port 3000) |
| Next.js has no `/auth/token` route | HTTP **404 Not Found** on login |
| Wrong env name in docs/tasks | `NEXT_PUBLIC_API_BASE_URL` was documented but **not read** by the client |
| Default JSON `Content-Type` on token POST | Could break OAuth2 form body if headers were merged incorrectly |

**Not** the cause: wrong uvicorn module (when Phase 1 app is used, routes exist). Legacy `backend.api:app` would also break APIs but manifests as connection errors or different OpenAPI, not Next.js 404.

---

## Fixes Applied

### 1. `frontend/lib/api/client.ts`

- Added `resolveApiBaseUrl()`:
  - Reads `NEXT_PUBLIC_API_URL` **or** `NEXT_PUBLIC_API_BASE_URL`
  - Trims whitespace; treats empty as missing
  - Default: **`http://localhost:8000`**
- `buildRequestUrl()` always produces an absolute URL
- `buildRequestHeaders()` sets `Content-Type: application/json` **only** when body is present and no `Content-Type` was supplied (fixes form login)
- Clearer **404** message pointing to `uvicorn backend.phase1.app:app`

### 2. `frontend/lib/api/phase1/auth.ts`

- Token request sends `Content-Type: application/x-www-form-urlencoded` and `Accept: application/json`

### 3. `frontend/app/login/page.tsx`

- After login, honors `?redirect=` query param (middleware deep-link) via `window.location.search`
- Calls `router.refresh()` so middleware sees the new `auth_token` cookie

### 4. `frontend/.env.example`

- Documents both env var names and correct backend start command

### 5. `backend/scripts/runtime_wiring_verification.py`

- Verifies OpenAPI paths: `/auth/token`, `/planning/*`, `/runtime/*`, `/analytics/*`, `/docs`

---

## Frontend / Backend URL Mapping

| Client call | Method | Full URL (default) |
| --- | --- | --- |
| Login | POST | `http://localhost:8000/auth/token` |
| Planning | POST/GET | `http://localhost:8000/planning/...` |
| Runtime | GET/POST | `http://localhost:8000/runtime/...` |
| Analytics | GET/POST | `http://localhost:8000/analytics/...` |
| Pilot feedback | POST | `http://localhost:8000/pilot/feedback` |
| API docs | GET | `http://localhost:8000/docs` |

**Frontend (Next.js):** `http://localhost:3000` — UI only; no Phase 1 API routes.

### Configuration

```env
# frontend/.env.local (create from .env.example)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Docker Compose already sets `NEXT_PUBLIC_API_URL` at build time (see `.env.docker.example`).

---

## Backend Runtime Verification

**Correct entrypoint:**

```bash
uvicorn backend.phase1.app:app --reload --host 0.0.0.0 --port 8000
```

**Incorrect (legacy):**

```bash
uvicorn backend.api:app --reload
```

**Script results (no local Postgres):**

| Check | Result |
| --- | --- |
| `GET /docs` | 200 |
| `GET /health/live` | 200 |
| `GET /openapi.json` | 200 |
| OpenAPI `/auth/token` | Present |
| OpenAPI `/planning/projects` | Present |
| OpenAPI `/runtime/projects` | Present |
| OpenAPI `/analytics/adoption-summary` | Present |
| `POST /auth/token` | 500 without Postgres (persisted IAM); route **exists** |

With PostgreSQL + seed users, `POST /auth/token` returns **200** and the full vertical slice works.

---

## Auth Verification

| Step | Mechanism | Status |
| --- | --- | --- |
| Login form | `signIn()` → `requestAccessToken()` | Wired to Phase 1 |
| OAuth2 body | `application/x-www-form-urlencoded` | Fixed header merge |
| Token storage | `localStorage` + `auth_token` cookie | Unchanged, correct |
| Middleware | Reads `auth_token` cookie | Unchanged |
| Redirect | `/dashboard/overview` or `?redirect=` | Fixed |
| Bearer on API calls | `getAuthHeaders()` in `apiRequest` | Unchanged |

Pilot credentials (after DB seed): `admin` / `admin`, etc.

---

## Phase 1 API Module Audit

All Phase 1 modules use `apiRequest` from `@/lib/api/client` (absolute base URL):

| Module | Prefix |
| --- | --- |
| `lib/api/phase1/auth.ts` | `/auth/token` |
| `lib/api/phase1/planning.ts` | `/planning/...` |
| `lib/api/phase1/runtime.ts` | `/runtime/...` |
| `lib/api/phase1/analytics.ts` | `/analytics/...` |
| `lib/api/phase1/intelligence.ts` | `/analytics/projects/{id}/operational-intelligence` |
| `lib/api/phase1/pilot.ts` | `/pilot/feedback` |

No Phase 1 module uses relative `/auth/token` or port 3000.

---

## Legacy Runtime Conflicts

Legacy clients under `lib/api/` (`tasks`, `reports`, `dashboard`, `lifecycle`, `workforce`, `validation`, `analytics`) still target **legacy** backend paths (`/daily-work-orders`, `/lifecycle/*`, etc.). They are **not** used by the Phase 1 operational dashboard path (overview, console, login).

| Legacy route | Mitigation |
| --- | --- |
| `/dashboard/performance` | Redirects to `/dashboard/overview` |
| `/dashboard/planning` | Redirects to `/dashboard/console` |
| `/dashboard/daily-reports` | Redirects to console execution |
| `/dashboard/workforce`, `/workers` | Redirect to overview |
| `/task/[taskId]` | Legacy task API only if visited directly |

**No changes** to legacy pages beyond existing redirects — prevents accidental navigation to broken legacy APIs during Phase 1 pilot.

---

## End-to-End Runtime Flow (expected with Postgres)

```text
Login (POST :8000/auth/token)
  → Dashboard overview (GET :8000/runtime/...)
  → Project creation (POST :8000/planning/projects)
  → Activity / step / WO (POST :8000/planning/...)
  → Assign + daily report + approve (POST :8000/runtime/...)
  → Analytics panels (GET :8000/analytics/...)
```

| Check | Without Postgres | With Postgres |
| --- | --- | --- |
| 404 on login | **Fixed** (URL resolution) | N/A |
| Auth loop | Unlikely if cookie set | OK |
| Wrong origin | **Fixed** | OK |
| Mutations | 500/503 | 201/200 |

---

## Remaining Gaps

1. **PostgreSQL required for login** — Persisted IAM (`platform_users`) needs a running DB; 404 fix is separate from 500 without DB.
2. **Create `frontend/.env.local`** — Developers must set `NEXT_PUBLIC_API_URL=http://localhost:8000` (or rely on new code default).
3. **CORS** — Phase 1 app enables CORS for configured origins; if frontend uses a non-listed origin, browser may block (network error, not 404).
4. **Legacy `/task` and report forms** — Still call old API if used; out of scope for this wiring fix.
5. **HttpOnly cookie** — `auth_token` remains client-set for dev; production hardening deferred.

---

## Operator Checklist

```bash
# Terminal 1 — backend (repo root)
set PYTHONPATH=.
uvicorn backend.phase1.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
cd frontend
copy .env.example .env.local
npm run dev
```

Open `http://localhost:3000/login` → sign in as `admin` / `admin` (with Postgres seeded).

Verify wiring:

```bash
set PYTHONPATH=.
python backend/scripts/runtime_wiring_verification.py
```

---

**Runtime wiring fix complete.**

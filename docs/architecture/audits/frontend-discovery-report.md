# BetavanX Frontend Discovery Audit

**Mode:** Read-only analysis. No code changed, no source files created or modified (this report is the only artifact).
**Scope:** `frontend/` (excluding `node_modules`).
**Date:** 2026-06-02
**Backend baseline:** Verified Phase 1 API — `/auth/token`, `/planning/*`, `/runtime/*` (UUID-based, OAuth2 password flow, JWT bearer).

---

## 1. Technology Stack

| Concern | Finding |
|---------|---------|
| Framework | **Next.js 16.1.6** (App Router, `frontend/app/`) |
| UI library / language | **React 19.2.3**, **TypeScript 5** (`strict: true`) |
| Styling | **Tailwind CSS v4** (`@tailwindcss/postcss`) + a large hand-written CSS layer in `app/globals.css` (class-based design system: `.button-primary`, `.input-base`, `.kpi-card`, `.planning-*`, etc.) |
| Icons | `lucide-react` (plus inline emoji/glyph icons in `navigation.ts`) |
| State management | **No Redux/Zustand/Jotai.** Local component state + custom hooks (`lib/hooks/useAsyncData`, `lib/hooks/useFormSubmit`) + a `useReducer`-style domain module (`modules/planning/usePlanningPrototype.ts`). i18n via React Context (`i18n/LanguageProvider`). |
| Data fetching | **No React Query / SWR.** Custom `fetch` wrapper `lib/api/client.ts` (`apiRequest`, `ApiError`) consumed through `useAsyncData`. |
| Routing | Next.js file-based App Router + `middleware.ts` (route matcher for `/dashboard`, `/task`, `/login`, `/auth`). |
| i18n | Custom bilingual system — **English + Persian/Farsi (RTL)**, `i18n/en/common.ts`, `i18n/fa/common.ts`, typed `CommonMessageKey`. |
| Build / lint | `next dev/build/start`, ESLint 9 + `eslint-config-next`. Path alias `@/* → ./*` (`tsconfig.json`). |

**Stack maturity:** modern and current (Next 16 / React 19). Cleanly TypeScript-typed throughout.

---

## 2. Folder Structure

```
frontend/
├── app/                         # Next.js App Router routes + layouts
│   ├── auth/ login/             # auth entry + login page
│   ├── dashboard/               # overview, daily-reports, daily-work-orders,
│   │                            #   planning, performance, workers, workforce
│   ├── task/[taskId]/           # dynamic task-detail route
│   ├── data/dashboard.json      # static mock dashboard payload
│   ├── layout.tsx / page.tsx    # root layout + landing page
│   └── globals.css              # design-system CSS
├── components/                  # presentational + composite UI
│   ├── ui/                      # Button, Card, Badge, Table, indicators, states
│   ├── layout/                  # AppShell, Sidebar, Topbar, primitives/ (grids, cards)
│   ├── dashboard/               # KpiSection, TasksSection, Trends/Analytics sections
│   ├── tables/                  # TasksTable, ReportsTable, WorkforceTable + table parts
│   ├── forms/                   # FormField/Input/Submit + CreateReportForm
│   ├── charts/                  # KPITrend, CostTrend, Productivity, Analytics cards
│   └── tasks/                   # task-specific cells
├── lib/
│   ├── api/                     # client.ts + per-domain clients (dashboard, reports,
│   │                            #   tasks, analytics, validation, lifecycle, workforce)
│   ├── auth/                    # session.ts, auth-client.ts, index.ts
│   ├── hooks/                   # useAsyncData, useFormSubmit
│   ├── operational/             # dashboardSummary, kpiMetrics, severity
│   ├── validation/              # zod-less schema helpers (report/workforce/common)
│   ├── charts/ design-tokens.ts navigation.ts
├── modules/                     # self-contained domain modules
│   ├── planning/                # in-memory planning prototype (data, types, hook)
│   └── workforce/
├── types/                       # DTO/type defs (dashboard, report, task, analytics,
│                                #   lifecycle, workforce, validation, common)
├── i18n/                        # en/ fa/ LanguageProvider config
├── public/                      # static svgs
└── middleware.ts next.config.ts tsconfig.json
```

**Purpose summary:** clear separation of routes (`app/`), presentation (`components/`), integration & utilities (`lib/`), domain modules (`modules/`), contracts (`types/`), and localization (`i18n/`).

---

## 3. Existing Pages

| Page | Route | Purpose | Data source | Status |
|------|-------|---------|-------------|--------|
| Landing | `/` | Marketing/entry, links to login + demo | Static | **Production Ready** (static) |
| Login | `/login` | Sign-in form | **Fake** — sets `localStorage.isLoggedIn`, no API call | **Placeholder** |
| Dashboard redirect | `/dashboard` | Redirects to `/dashboard/overview` | — | Production Ready (trivial) |
| Overview | `/dashboard/overview` | KPI command center (KPIs, recommendation, tasks, trends, BIM placeholder) | `GET /dashboard` (legacy) | **Partial** (works vs legacy backend; BIM panel is placeholder) |
| Daily Reports | `/dashboard/daily-reports` | List + create daily reports | `GET /daily-reports`, `POST /daily-report` (legacy) | **Partial** |
| Daily Work Orders | `/dashboard/daily-work-orders` | Work-order list | `GET /daily-work-orders` (legacy) | **Partial** |
| Planning | `/dashboard/planning` | WBS templates, location tree, activity instantiation, dependencies, drag Gantt, progress logs | **100% in-memory** (`usePlanningPrototype`) — no backend | **Partial** (rich prototype, zero persistence) |
| Performance | `/dashboard/performance` | KPI/analytics trends | `analytics` client (legacy) | **Partial** |
| Workers | `/dashboard/workers` | Workforce list/intelligence | `workforce` client (legacy/extension) | **Partial** |
| Workforce | `/dashboard/workforce` | Workforce extension dashboard | `workforce` client | **Partial** |
| Task Detail | `/task/[taskId]` | Task lifecycle/readiness/timeline | `tasks` + `lifecycle` clients, **numeric `taskId`** | **Partial** |

**No truly dead routes**, but several are placeholder/legacy-bound (login, BIM viewer panel, planning persistence).

---

## 4. Existing Components

Strong, reusable presentational layer. Highlights:

| Component(s) | Purpose | Quality | Reusability |
|--------------|---------|---------|-------------|
| `layout/AppShell`, `Sidebar`, `Topbar`, `PlatformShell`, `EngineStatusPanel` | App chrome / navigation shell | Good, collapsible, i18n-driven | **High** (backend-agnostic) |
| `layout/primitives/*` (`DashboardGrid`, `KPIGrid`, `SectionContainer`, `CompactCard`, `DenseTableWrapper`) | Layout building blocks | Good | **High** |
| `ui/*` (`Button`, `Card`, `Badge`, `Input`, `Table`, `ProgressBar`, `EmptyState`, `LoadingState`, `ErrorState`, `PageHeader`, `PageLoader`, `AsyncPageContent`) | Primitive UI kit + async states | Good, consistent | **High** |
| `ui/*Indicator` (`Health`, `Risk`, `Readiness`, `Blocker`, `Trust`, `Severity`) | Operational status visuals | Good | **High** (presentational) |
| `tables/*` (`TasksTable`, `ReportsTable`, `WorkforceTable`, `TableHead/Row/Cell/Wrapper`) | Data tables | Good, composable | **Medium-High** (bound to legacy row shapes) |
| `forms/*` (`FormField`, `TextInput`, `SelectInput`, `TextareaInput`, `SubmitButton`, `CreateReportForm`, `FormError/Success`) | Form kit + report form | Good | **High** (kit) / **Medium** (`CreateReportForm` bound to legacy payload) |
| `charts/*` (`KPITrendChart`, `CostTrendChart`, `ProductivityChart`, `AnalyticsCard`) | Lightweight charts (sparkline util) | Good, dependency-free | **High** |
| `dashboard/*` sections (`KpiSection`, `TasksSection`, `TrendsSection`, `AnalyticsSection`, `WorkforceIntelligenceSection`, `RecommendationSection`, `StatCard`, `DashboardHeader`) | Composed dashboard blocks | Good | **Medium** (bound to legacy `DashboardData`) |

**Duplication noted (debt):** `StatusBadge` (`components/StatusBadge.tsx` **and** `components/ui/StatusBadge.tsx`), `ProgressBar` (`components/ProgressBar.tsx` **and** `components/ui/ProgressBar.tsx`), `EmptyState` (`components/ui/EmptyState.tsx` **and** `components/tables/EmptyState.tsx`), and overlapping `KpiCard` vs `dashboard/StatCard`.

---

## 5. Existing Data Flow

| Element | Finding |
|---------|---------|
| API client | `lib/api/client.ts` → `apiRequest()`; base URL `process.env.NEXT_PUBLIC_API_URL ?? http://127.0.0.1:8000`; JSON; injects `Authorization` via `getAuthHeaders()`; normalizes FastAPI `detail` errors (already FastAPI-aware ✔). |
| Domain clients | `dashboard, reports, tasks, analytics, validation, lifecycle, workforce` — all target **legacy** endpoints: `/dashboard`, `/daily-reports`, `/daily-report`, `/daily-work-orders`, `/task/{id}`, `/lifecycle/*`, `/validation/*`, `/workforce/*`. |
| Mock data | `app/data/dashboard.json` (static dashboard payload); planning page is entirely in-memory. |
| Local state | Per-page React state + `useAsyncData`/`useFormSubmit`. |
| Global state | Only i18n context. No app-wide store. |
| Hardcoded data | `modules/planning/data.ts` (WBS templates, project/location/resource types), `navigation.ts`, engine-status items. |

**Does the frontend currently talk to a backend? → YES**, but to the **legacy** backend (`backend/api.py` routers), **not** the verified Phase 1 API. Endpoints, payload shapes, and **numeric IDs** differ from Phase 1 (UUIDs).

---

## 6. Existing Authentication

| Element | Finding |
|---------|---------|
| Login page | `/login` — collects **email + password**, performs **no API call**, just `setSessionActive(true)` → `localStorage.isLoggedIn="true"` and redirects. |
| Auth client | `lib/auth/auth-client.ts` — **placeholder**: `login()` returns `{ accessToken: "" }`, `refresh/logout` are no-ops. |
| Token handling | `lib/auth/session.ts` — reads/writes `localStorage.auth_token`; `getAuthHeaders()` emits `Authorization: Bearer <token>` (✔ compatible shape) but a real token is never stored. |
| Route guards | `middleware.ts` — guard logic is **commented out** ("enable when JWT/cookie auth is implemented"); currently lets all matched routes pass. |
| Roles | `UserRole = "admin" | "manager" | "engineer" | "viewer"`. |

**Compatibility with Phase 1 Auth Layer:** **Low / incompatible as-is.**
- Phase 1 issues JWT via `POST /auth/token` using **OAuth2 password flow (form-encoded `username`/`password`)**; frontend uses **email** and never calls it.
- Phase 1 roles are `admin / supervisor / worker / investor`; frontend roles are `admin / manager / engineer / viewer` → **mismatch**.
- **Reusable parts:** the bearer-token plumbing (`getAuthHeaders`, `auth_token` storage) and the middleware matcher skeleton are directly extendable once a real login call is wired.

---

## 7. Existing Dashboard vs Phase 1 Runtime Chain

Mapping current UI against `Project → ActivityInstance → WorkflowStep → WorkOrder → DailyReport → Progress`:

| Phase 1 entity | Current representation | Verdict |
|----------------|------------------------|---------|
| **Project** | No first-class Project concept (planning prototype has a local "project"; overview is project-agnostic) | **Incompatible** (needs project context/selector) |
| **ActivityInstance** | Legacy "tasks" + planning "activities" (different shapes, numeric/local IDs) | **Partially usable** (UI yes, contract no) |
| **WorkflowStep** | **Not represented** (planning has activities, not workflow steps; no status machine UI) | **Incompatible** (missing) |
| **WorkOrder** | `/dashboard/daily-work-orders` (legacy shape, numeric id) | **Partially usable** (UI yes, contract no) |
| **DailyReport** | `/dashboard/daily-reports` + `CreateReportForm` | **Partially usable** (closest match; payload differs) |
| **Progress** | Planning prototype computes client-side; overview shows legacy KPIs | **Partially usable** (UI yes; must consume `/runtime` dashboards) |

**Overall dashboard verdict: Partially usable.** The visual/component layer is strong and reusable; the **data contracts and entity model are legacy-shaped** and do not match the Phase 1 runtime chain. There is **no WorkflowStep UI** and **no Project-scoped dashboard** consuming `/runtime/projects/{id}/dashboard`.

---

## 8. Backend Integration Readiness

**Can the current frontend consume `/planning/*`, `/runtime/*`, `/auth/token` without major redesign? → NO.**

Blockers:
1. **Endpoint mismatch** — every API client targets legacy routes (`/dashboard`, `/daily-report`, `/lifecycle/*`, `/workforce/*`), none target `/planning` or `/runtime`.
2. **ID model mismatch** — frontend uses **numeric** IDs (`taskId: number`, `/task/${taskId}`); Phase 1 uses **UUIDs**.
3. **Payload/shape mismatch** — `types/*` reflect legacy DTOs, not Phase 1 Read schemas (`ProjectRead`, `ActivityInstanceRead`, `WorkflowStepRead`, `WorkOrderRead`, `DailyReportRead`).
4. **Auth flow mismatch** — no OAuth2 password login call; fake login; role vocabulary differs.
5. **No WorkflowStep / project-scoped runtime views.**

What is **already compatible / low-effort**:
- The `apiRequest` wrapper (base URL env, JSON, FastAPI error normalization, Bearer header injection) is a solid foundation — only new typed client functions + types are needed.
- Bearer-token storage and the middleware matcher are reusable once login is wired to `/auth/token`.

**Verdict:** the **integration layer must be rebuilt**; the **presentation layer can be largely reused**.

---

## 9. Technical Debt (identified, not fixed)

- **Dead/placeholder logic:** `auth-client.ts` (stub returning empty token), fake `/login`, disabled guard in `middleware.ts`, BIM-viewer placeholder panel, `app/data/dashboard.json` mock.
- **Duplicated components:** `StatusBadge` ×2, `ProgressBar` ×2, `EmptyState` ×2, `KpiCard` vs `dashboard/StatCard`.
- **Two parallel architectures:** legacy-bound API/dashboard stack **and** a standalone in-memory planning prototype that share no data path.
- **Obsolete/legacy coupling:** numeric task IDs; `lifecycle`, `validation`, `workforce` clients map to legacy/extension endpoints absent from the Phase 1 contract.
- **Role vocabulary drift:** `manager/engineer/viewer` (FE) vs `supervisor/worker/investor` (BE).
- **Broken assumption:** middleware "protects" routes but auth is never enforced (any visitor can reach `/dashboard/*`).

---

## 10. Frontend Readiness Score

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **UI Layer** | **80%** | Rich, consistent component kit; bilingual (en/fa, RTL); design tokens; polished CSS. |
| **Architecture** | **70%** | Clean route/component/lib/module separation, typed, custom hooks; some duplication & dual architectures. |
| **Backend Compatibility** | **20%** | Endpoints, ID model, payloads, and auth all mismatch Phase 1; only the fetch wrapper aligns. |
| **Reuse Potential** | **75%** | Presentation, shell, forms, tables, charts, i18n, tokens are reusable; integration/types are not. |
| **Technical Debt** | **35%** | Moderate: dead auth, duplicates, legacy coupling, dual architecture. |
| **Overall Frontend Readiness** | **≈ 48%** | Strong UI shell on top of an incompatible/legacy data + auth layer. |

---

## Final Recommendation

**1. Can the current frontend be reused?**
Yes — **partially**. The presentation/UX layer is reusable; the data-integration and auth layers must be rebuilt for Phase 1.

**2. What percentage can be reused?**
Roughly **70–75%** of the UI/presentation and scaffolding (Next.js setup, component kit, layout/shell, charts, forms, i18n, design tokens, `apiRequest` core). Roughly **20–25%** of the data/integration/auth layer is reusable.

**3. What should be kept?**
- Next.js 16 + React 19 + TS + Tailwind v4 scaffolding.
- `components/ui`, `components/layout` (+ primitives), `components/charts`, `components/forms` kit, `components/tables` parts.
- `i18n/` (en/fa), `lib/design-tokens.ts`, `globals.css`.
- `lib/api/client.ts` (`apiRequest`) and the Bearer/session plumbing (`lib/auth/session.ts`).
- The planning page as a **UX reference** for the eventual `/planning` integration.

**4. What should be discarded / rewritten?**
- `lib/auth/auth-client.ts` stub and the fake `/login` flow → replace with real OAuth2 `POST /auth/token`.
- Legacy domain clients tied to non-Phase-1 endpoints (`lifecycle`, `validation`, `workforce`, numeric-`task` clients) — retire or quarantine unless the legacy backend is retained.
- `types/*` legacy DTOs → replace with Phase 1 Read/Create schema types (UUID-based).
- Duplicated components (consolidate to single `ui/` versions).
- `app/data/dashboard.json` mock and the in-memory-only planning state path.

**5. What should be the next frontend stage?**
**Stage F1 — Phase 1 Integration Layer (foundation, no redesign of visuals):**
1. New typed API clients for `/auth/token`, `/planning/*`, `/runtime/*` reusing `apiRequest`.
2. Phase 1 TypeScript types mirroring the verified Read/Create schemas (UUIDs).
3. Real OAuth2 password login → store JWT → enable the `middleware.ts` guard; align roles to `admin/supervisor/worker/investor`.
4. Introduce a **Project context/selector** and a **project-scoped runtime dashboard** consuming `/runtime/projects/{id}/dashboard`.
5. Add the missing **WorkflowStep** views and wire planning forms to `/planning/*`.
6. Consolidate duplicate components and remove dead legacy clients.

> Subsequent stages can then progressively re-skin the existing dashboard/tables/forms onto the new Phase 1 contracts, reusing the kept presentation layer.

---

*Audit only — no code changes, no commits, no file modifications beyond this report.*

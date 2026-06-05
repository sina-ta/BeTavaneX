# Frontend Theme Cleanup Report

**Type:** Post-migration consistency audit (light theme + RTL)  
**Scope:** CSS organization, design tokens, RTL stability — no visual redesign  
**Date:** 2026-06-04

---

## Executive summary

After the light-theme and RTL Persian migration, the frontend had **overlapping CSS layers**, **legacy dark-era classes**, and **drift between JS tokens and CSS variables**. This pass consolidates tokens, removes dead styles, deduplicates grids/inputs, and tightens RTL without changing routes, APIs, or business logic.

`npm run build` passes after cleanup.

---

## Issues found (before cleanup)

| Category | Finding |
| --- | --- |
| Duplicate surfaces | `--bg-primary` and `--bg-page` both set to `#f4f6f9` independently |
| Duplicate typography | `typography.css` defined `.page-title` (42px) conflicting with `design-system.css` (22px via token) |
| Duplicate grids | `.kpi-grid` defined in both `design-system.css` and `layout-primitives.css` |
| Duplicate inputs | `.form-input` in `globals.css` and `.input-base` in `design-system.css` (same purpose) |
| Split sidebar CSS | Sidebar rules split across `theme.css` and `command-center.css` with duplicate `.sidebar-root` positioning |
| Dead dark remnants | `planning-prototype.css`: `rgba(15, 23, 42, …)` card backgrounds; Tailwind `slate-*` / `text-slate-400` in progress/trend UI |
| RTL overrides | Redundant `html[dir="rtl"]` tree indent rules after physical `margin-left` on tree nodes |
| JS/CSS drift | `lib/design-tokens.ts` still reflected pre-light shell sizes (220px sidebar, 12px page gap) |
| Inline hex | Operational panels used `#94a3b8` instead of `--text-muted` |

---

## Changes applied

### 1. Token consolidation (`styles/theme.css`)

- **Single source of truth** for colors, spacing, typography, shadows.
- `--bg-primary` now aliases `--bg-page` (no duplicate hex).
- Added semantic tokens:
  - `--status-unknown`, `--trend-*`, `--text-error`
  - `--brand-gradient`, `--brand-gradient-auth`
  - `--border-focus`, `--focus-ring`, `--overlay-blue-*`
  - `--kpi-*-bg`, `--shadow-tint`, `--shadow-topbar`
- **Removed** component rules from `theme.css` (tokens only).

### 2. CSS file organization

| File | Role after cleanup |
| --- | --- |
| `theme.css` | `:root` tokens only |
| `design-system.css` | Pages, KPIs, tables, forms, buttons, badges, progress fills |
| `layout-primitives.css` | Grids/cards; KPI column modifiers only (`--2`, `--3`) |
| `utilities.css` | **New** — cross-cutting utilities (links, emphasis, KPI icons, trends) |
| `command-center.css` | Shell: sidebar, topbar, auth, slice-nav |
| `planning-prototype.css` | Planning UI (tokenized) |
| `globals.css` | Reset, imports, RTL document rules |

**Removed:** `styles/typography.css` (unused legacy `.card-title` / conflicting `.page-title`).

**Import order** (`globals.css`):

```text
theme → design-system → layout-primitives → utilities → command-center → planning-prototype
```

### 3. Duplication removed

| Item | Resolution |
| --- | --- |
| `.kpi-grid` base grid | Kept in `design-system.css` only |
| `.form-input` / `.input-base` | Merged in `design-system.css`; `.input-base` remains as alias for login/Input |
| `.button-submit` | Moved from `globals.css` to `design-system.css` |
| Sidebar component styles | Consolidated in `command-center.css` (single `.sidebar-root` block) |
| Platform utilities | Moved to `utilities.css` |

### 4. Dark-theme remnant removal

| Location | Before | After |
| --- | --- | --- |
| `planning-prototype.css` cards | `rgba(15, 23, 42, 0.25)` | `var(--bg-muted)` |
| `ProgressBar.tsx` | `bg-slate-500`, `bg-green-500`, … | `progress-bar-fill--*` classes |
| `severity.ts` trends | `text-slate-400`, `text-green-400` | `trend-stable`, `trend-improving`, `trend-declining` |
| Operational panels | `#94a3b8` | `var(--status-unknown)` |
| Auth/login errors | `#f87171` | `var(--text-error)` |

### 5. RTL stability

| Area | Change |
| --- | --- |
| Tables | `text-align: start` / `end` instead of left/right in `globals.css` |
| Planning tree | `margin-inline-start`, `padding-inline-start`, `border-inline-start` (removed redundant RTL override block) |
| Planning cards | `text-align: start` |
| Operational panels | `marginRight` → `marginInlineEnd` where found |
| Shell | Platform/sidebar margins already used `margin-inline-start` (unchanged) |

### 6. JS layout tokens (`lib/design-tokens.ts`)

Synced numeric values with `:root`:

- `pageGap` 16, `cardPadding` 16, `sidebarWidth` 240, `topbarHeight` 56, table row/padding, typography scale.

---

## Spacing & typography normalization

### Spacing (canonical)

| Token | Value | Usage |
| --- | --- | --- |
| `--space-1` … `--space-6` | 4–24px | Component padding/gaps |
| `--section-gap` | 12px | Grid/card gaps |
| `--page-gap` | 16px | Page vertical rhythm |
| `--card-padding` | 16px | Cards, compact panels |

### Typography (canonical)

| Token / class | Size | Usage |
| --- | --- | --- |
| `--font-page-title` / `.page-title` | 22px | `PageHeader` h1 |
| `--font-section-title` / `.compact-card__title` | 14px | Section/card headers |
| `--font-metric` / `.kpi-value` | 28px | KPI values |
| `--font-size-sm` | 13px | Body, inputs, nav |
| Locale fonts | Vazirmatn (fa), Geist (en) | `globals.css` + `layout.tsx` |

**Rule:** Do not reintroduce ad-hoc `font-size: 42px` titles; use tokens or `.page-title`.

---

## Color variable map (quick reference)

| Variable | Purpose |
| --- | --- |
| `--bg-page` | App background |
| `--bg-card` / `--bg-secondary` | Cards, topbar |
| `--bg-muted` | Subtle panels, search field |
| `--text-primary` / `--secondary` / `--muted` | Text hierarchy |
| `--blue-primary` / `--blue-soft` | Actions, active nav |
| `--border-color` / `--border-focus` | Borders, hover focus |
| `--shadow-card` / `--shadow-sidebar` / `--shadow-topbar` | Elevation |
| `--brand-gradient` | Logo, avatar |

---

## Verification

```bash
cd frontend && npm run build
```

Manual checks (recommended):

1. `/dashboard/console` — RTL sidebar right, KPI row, forms readable.
2. `/dashboard/overview` — operational panels, tables align end in FA.
3. `/login` — inputs use light `.input-base` / `.form-input` styling.
4. Toggle EN ↔ FA — direction and fonts switch without layout break.

---

## Remaining gaps (low risk, optional follow-up)

| Item | Notes |
| --- | --- |
| `components/layout/AppShell.tsx` | Unused legacy shell; still references `--bg-primary` (alias works). Safe to delete file when confirmed unused. |
| `section-card` vs `compact-card` | Two card patterns in `design-system.css`; merge naming in a future pass if `section-card` is unused. |
| `command-grid-2/3` | Legacy aliases in `command-center.css`; prefer `DashboardGrid` primitives in new pages. |
| Inline `style={{}}` on operational/overview pages | Some layout gaps remain; prefer `.stack-sm` / tokens where touched. |
| Tailwind in `Sidebar.tsx` | `flex`, `mb-3` utilities coexist with CSS shell; acceptable, not migrated to avoid churn. |
| Auth brand panel hex in gradient | Defined once in `--brand-gradient-auth` token (acceptable). |

---

## Files changed (this audit)

| File | Action |
| --- | --- |
| `styles/theme.css` | Tokens only; expanded semantic vars |
| `styles/utilities.css` | **Created** |
| `styles/typography.css` | **Deleted** |
| `styles/design-system.css` | Merged inputs/buttons/progress; typography canonical |
| `styles/layout-primitives.css` | Removed duplicate `.kpi-grid` |
| `styles/command-center.css` | Sidebar consolidated; tokenized gradients/shadows |
| `styles/planning-prototype.css` | Light surfaces; logical RTL tree |
| `app/globals.css` | Slim imports + RTL; utilities extracted |
| `lib/design-tokens.ts` | Synced with CSS |
| `components/ui/ProgressBar.tsx` | Token-based fill classes |
| `lib/operational/severity.ts` | Trend utility classes |
| `components/operational/*.tsx` | `var(--status-unknown)`; logical margins |
| `app/login/page.tsx` | Error color token |

---

## Maintainer guidelines

1. **New colors** → add to `theme.css` only; reference via `var(--*)` in CSS or `var(--*)` in inline styles.
2. **New spacing** → use `--space-*` or `--section-gap` / `--page-gap`; avoid magic `12px` in new CSS.
3. **Forms** → use class `form-input` (or alias `input-base`).
4. **RTL** → prefer logical properties (`margin-inline-*`, `padding-inline-*`, `text-align: start`).
5. **Do not** re-add `typography.css` or dark `slate-*` Tailwind on operational surfaces.

---

**Frontend theme cleanup complete.**

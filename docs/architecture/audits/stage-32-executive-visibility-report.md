# Stage 32 — Executive Operational Awareness & Strategic Visibility Report

**Stage:** 32 — Executive Operational Awareness & Strategic Visibility  
**Type:** Low-noise executive compression over Stage 31 (no BI platform, no ML narratives)  
**Prerequisites:** Stages 27–31 (telemetry, project intelligence, decision support, coordination, organizational intelligence)

---

## Executive Summary

Stage 32 adds a **compressed executive operational layer** for leadership: portfolio execution health, strategic risk surfaces, evidence-based trend narratives, leadership attention ordering, and organizational pressure indicators. Delivery is **`GET /analytics/executive-visibility`** plus a compact **Executive operational awareness** card on Overview — **admin and investor only**; workers never see it; supervisors retain Stage 31 organizational detail without executive compression.

| Capability | Status |
| --- | --- |
| Executive attention compression | Implemented |
| Portfolio execution health | Implemented |
| Strategic operational risk surfaces | Implemented |
| Execution trend narratives (evidence-based) | Implemented |
| Leadership attention prioritization | Implemented |
| Organizational pressure visibility | Implemented |
| Executive UI layer (role-gated) | Implemented |
| Verification | `stage32_verification.py`, CI workflow |

---

## 1. Executive Attention Findings

### Design intent

Executives need **what is deteriorating, what is stable, what needs intervention** — not metric walls. Stage 32 caps surfaced lists at **5–6 items** and leads with a two-sentence `executive_summary` plus at most **five** `strategic_attention` lines.

### Compression mechanics

| Input (Stage 31) | Executive output |
| --- | --- |
| `organizational_attention` (up to 8 lines) | Merged into `strategic_attention` after summary + top 3 priorities |
| Bottlenecks + cross-project + coordination + culture | Deduped `strategic_risks` (severity-sorted, max 6) |
| Maturity/capacity bands | Single `portfolio_health.overall_band` (HEALTHY / STABLE / CAUTION / CRITICAL) |
| Project snapshots | `deteriorating_project_codes` / `stable_project_codes` (max 6 each) |

### Attention-fatigue controls

- No new KPI grid or chart library.
- Details hidden behind `<details>` in UI (risks, narratives, pressure).
- Supervisors **do not** call the executive endpoint — avoids duplicate cognitive load with org panel.

### Finding

Compression is **useful at pilot scale** when PostgreSQL and ≥2 projects exist; with zero projects the layer degrades gracefully with the same empty-org messaging as Stage 31.

---

## 2. Portfolio Health Findings

### Portfolio band heuristic

| Band | Typical triggers |
| --- | --- |
| **CRITICAL** | ≥2 AT_RISK projects, or maturity STRAINED, or capacity SATURATED |
| **CAUTION** | Any AT_RISK, ≥2 ATTENTION, capacity PRESSURED, maturity EMERGING/STRAINED |
| **HEALTHY** | maturity ESTABLISHED/DEVELOPING + capacity BALANCED |
| **STABLE** | Default when no escalation triggers |

### Distributions exposed

- `health_distribution` — Stage 28 bands (GOOD, ATTENTION, AT_RISK) per accessible project.
- `coordination_pressure_distribution` — low / medium / high from Stage 31 snapshots.
- Org-level `maturity_band` and `capacity_band` echoed for executive context.

### Healthy vs deteriorating zones

- **Hotspots:** projects with AT_RISK/ATTENTION health or **high** coordination pressure.
- **Stable zones:** GOOD health with low/medium pressure.

### Explainability

Every portfolio summary string cites **counts and bands**, not predictive ML. Investors can read portfolio band without opening per-project console metrics.

---

## 3. Strategic Operational Risks

### Risk sources (organization-level)

Risks are merged from Stage 31 with deduplication by `signal_type`:

| Category | Example signal types |
| --- | --- |
| Approval saturation | `chronic_approval_congestion`, `approval_bottleneck_pattern` |
| Blocker accumulation | `blocker_choke_point`, `recurring_blocker_types` |
| Coordination instability | `coordination_failure_pattern`, `competing_project_attention` |
| Execution fragmentation | `execution_drift`, `operational_imbalance` |
| Reporting degradation | `reporting_inconsistency`, `reactive_execution` |
| Supervisor overload | `supervisor_overload_concentration` (audit concentration, not HR) |

### Prioritization

`critical` severity risks surface first in `strategic_risks` and drive **immediate** `leadership_priorities` when present.

### Strategic vs tactical

Executive risks are **org-wide**; project supervisors still use Stage 28–30 on the selected project. Escalation path: executive hotspot code → Stage 28 project intelligence.

---

## 4. Execution Trend Narratives

### Rules (no fake AI storytelling)

Narratives are **template sentences** bound to observable evidence:

| narrative_id | When generated | Evidence |
| --- | --- | --- |
| `coordination_pressure_cluster` | ≥2 high-pressure projects | Snapshot pressure heuristic |
| `approval_saturation` / `approval_delay_easing` | Chronic approval congestion + audit week buckets | Stage 31 bottlenecks + `operational_audit.jsonl` approve counts (7d vs prior 7d) |
| `approval_throughput_up` | Overdue pattern + rising approvals | Audit comparison |
| `maturity_deterioration_hotspots` | EMERGING/STRAINED maturity + AT_RISK projects | Maturity score + snapshot bands |
| `assignment_surge_capacity` | Assignments up >50% WoW + PRESSURED capacity | Audit assign counts + capacity band |
| `portfolio_stable_narrative` | Fallback when no trend triggers | Explicit “current-state only” evidence |

### Trend direction field

`improving` | `stable` | `worsening` | `unknown` — supports scanability without charts.

### Limitation

Without sufficient audit JSONL history, narratives default to **current-state** or stable fallback; `false_positive_notes` documents this.

---

## 5. Leadership Prioritization Findings

### Ordering logic

`leadership_priorities` (max 6) are built in rank order:

1. Portfolio **CRITICAL** → immediate executive review.
2. Capacity **SATURATED** → defer new assignments.
3. Each **critical** strategic risk → bottleneck clearance focus.
4. Maturity **EMERGING/STRAINED** → planned discipline improvements.
5. Hotspot project codes → planned Stage 28 deep-dives.
6. Supervisor **concentration_risk** → monitor load distribution.

Each item includes `attention_level` (`immediate` | `planned` | `monitor` | `stable`), `evidence`, and `suggested_focus` for intervention usefulness.

### Intervention usefulness

Priorities map to **concrete next steps** (clear queues, review AT_RISK projects, distribute audit load) rather than generic “improve KPIs.”

---

## 6. Organizational Pressure Findings

### Pressure indicators surfaced

| indicator_type | Meaning |
| --- | --- |
| `execution_capacity` | Stage 31 capacity band PRESSURED/SATURATED |
| `approval_congestion` | Chronic approval bottleneck |
| `blocker_density` | Org-wide open blocker choke |
| `coordination_overload` | Stalled steps exceed project count heuristic |
| `supervisor_overload_concentration` | Audit share ≥60% on one account |
| `operational_fragmentation` | Reporting + reactive governance culture signals |

### Stress visibility

Pressure block answers: **where is the organization stressed** and **whether intervention may be required soon** (via severity + capacity band), without duplicating full Stage 31 signal lists in the default view.

---

## 7. Executive Visibility Effectiveness

### API

| Item | Value |
| --- | --- |
| Endpoint | `GET /analytics/executive-visibility` |
| Roles | `admin`, `investor` |
| Denied | `worker`, `supervisor` |
| Composition | `build_executive_visibility` → `build_organizational_intelligence` (single DB pass via org service) |

### UI

| Item | Value |
| --- | --- |
| Component | `ExecutiveVisibilityPanel` on `/dashboard/overview` |
| Policy | `canViewExecutiveVisibility()` |
| Placement | Above `OrganizationalIntelligencePanel` for admin/investor |

### Strategic usefulness checklist

| Criterion | Assessment |
| --- | --- |
| Low-noise | Pass — capped lists, summary-first |
| Explainable | Pass — evidence fields on narratives/risks |
| Portfolio health | Pass — band + distributions + hotspots |
| Actionable prioritization | Pass — ranked priorities with suggested_focus |
| No enterprise-dashboard collapse | Pass — no new chart stack or ERP modules |

### Signal clarity

Executives see **one portfolio band** and **≤5 attention lines** before expanding details — suitable for investor read-only and admin escalation reviews.

---

## 8. False-Positive / Noise Analysis

| Risk | Mitigation |
| --- | --- |
| Single-pilot mimics org concentration | Inherited Stage 31 notes + executive cap on list sizes |
| Audit WoW trends with sparse JSONL | Fallback stable narrative; note in `false_positive_notes` |
| AT_RISK conflated with portfolio CRITICAL | Requires ≥2 AT_RISK or STRAINED/SATURATED for CRITICAL band |
| Duplicate supervisor vs executive views | Supervisors blocked from executive endpoint |
| Re-running org intel twice per request | Acceptable at pilot scale; org capped at `ORG_INTEL_MAX_PROJECTS` |
| Investor sees both executive + org panels | Intentional: executive compresses; org remains explainable drill-down |

### Attention-fatigue risk

**Low** for admin/investor if they use default collapsed sections; **medium** if both executive and org panels expanded simultaneously — recommend executives rely on executive card first.

---

## 9. Recommended Stage 33

**Operational resilience & continuity visibility** (suggested direction, not implemented):

- Time-bounded recovery signals after incidents (blocker spikes, approval freezes).
- Cross-stage “intervention outcome” hints (did approval throughput improve after supervisor focus).
- Optional email/export hook for investor reporting — still JSON/API-first, no BI suite.
- Hardening: cache org snapshot for executive endpoint if project count grows past pilot caps.

Stop after Stage 32 per program scope.

---

## Artifacts

| Artifact | Path |
| --- | --- |
| Service | `backend/phase1/analytics/executive_visibility_service.py` |
| Schema | `backend/phase1/schemas/executive_visibility_schema.py` |
| API | `GET /analytics/executive-visibility` |
| Frontend API | `frontend/lib/api/phase1/analytics.ts` |
| UI | `frontend/components/operational/ExecutiveVisibilityPanel.tsx` |
| Role policy | `frontend/lib/auth/role-policy.ts` (`canViewExecutiveVisibility`) |
| Scripts | `stage32_verification.py`, `stage32_runtime_verification.py` |
| CI | `.github/workflows/stage32-ci.yml` |

---

## Verification

```bash
PYTHONPATH=. python backend/scripts/stage32_verification.py
PYTHONPATH=. python backend/scripts/stage32_runtime_verification.py
cd frontend && npm run build
```

Degraded pass (exit 0) when PostgreSQL unavailable — same pattern as Stages 28–31.

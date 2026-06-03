# Stage 28 — Operational Intelligence & Predictive Runtime Report

**Stage:** 28 — Operational Intelligence & Predictive Runtime  
**Type:** Explainable heuristics over runtime data (no ML, no new domain entities)  
**Prerequisites:** Stages 25–27 (pilot, ergonomics, adoption JSONL)

---

## Executive Summary

Stage 28 adds **explainable operational intelligence**: project health scoring, stagnation and approval-delay signals, blocker trends, lightweight anomaly detection, and forecast hints — all derived from PostgreSQL runtime tables plus Stage 27 JSONL mirrors. No black-box scores, no enterprise AI stack.

| Capability | Delivery |
| --- | --- |
| Project health (0–100 + band) | Heuristic components with documented deductions |
| Stagnation detection | Stale steps, rework, inactive work orders |
| Approval intelligence | Pending age, backlog vs reports |
| Blocker trends | Open count, type mix, long-lived |
| Runtime anomalies | Audit/usage heuristics (conflicts, bursts, starvation) |
| Predictive signals | Rule-based forecasts with confidence + reason |
| Attention layer | Overview **Operational attention** panel |
| API | `GET /analytics/projects/{id}/operational-intelligence` |

---

## 1. Operational Intelligence Signals

### Signal taxonomy

| Category | `signal_type` examples | Severity rules |
| --- | --- | --- |
| Stagnation | `stalled_workflow_steps`, `rework_required_steps`, `inactive_work_orders` | warning / info |
| Approval | `delayed_pending_approvals`, `approval_backlog_vs_reports` | critical if ≥3 delayed |
| Blockers | `open_blockers`, `long_lived_blockers` | critical if HIGH/CRITICAL open |
| Anomalies | `concurrency_spike`, `duplicate_reporting_spike`, `workflow_starvation`, `inactive_dashboard`, `approval_burst` | info–warning |
| Predictions | `likely_stalled_approval`, `approval_backlog_risk`, `likely_delayed_workflow`, `operational_backlog_risk` | confidence low/medium/high |

### Configuration (environment)

| Variable | Default | Meaning |
| --- | --- | --- |
| `OPS_STALL_DAYS` | 7 | Step/WO inactivity threshold |
| `OPS_APPROVAL_DELAY_DAYS` | 5 | Pending approval age threshold |

---

## 2. Workflow Stagnation Findings

### Detection logic

| Condition | Interpretation |
| --- | --- |
| Step status ∈ {PLANNED, IN_PROGRESS, INSPECTION_PENDING, REWORK_REQUIRED} and `updated_at` older than `OPS_STALL_DAYS` | Workflow inactive too long |
| Status = REWORK_REQUIRED | Step reopened / rework path |
| Work order CREATED/ASSIGNED with stale `updated_at` | Assignment without execution progress |

### Baseline (Stages 25–26)

Planning chain length still causes **pre-execution stagnation** (many PLANNED, zero IN_PROGRESS) — surfaced as `workflow_starvation` anomaly when ≥5 PLANNED and 0 IN_PROGRESS.

### False-positive risk

- Legitimate waiting periods (weather, permits) appear as stalled steps.
- Demo seed data with old timestamps triggers signals without live pilot.

---

## 3. Approval-Delay Analysis

### Metrics

| Metric | Computation |
| --- | --- |
| Delayed pending | Approvals PENDING/UNDER_REVIEW with `updated_at` before cutoff |
| Backlog ratio | `pending_approvals` count vs `daily_reports` in last 7 days |
| Approval burst | ≥4 approve audits same day (JSONL) |

### Findings (expected in live pilot)

| Pattern | Supervisor impact |
| --- | --- |
| Reports ↑, approvals flat | Field work digitized; sign-off lagging |
| Delayed pending ≥3 | Hotspot for supervisor workload |
| Same-day approval burst | Catch-up after delay (not necessarily negative) |

---

## 4. Blocker Trend Findings

| Signal | Logic |
| --- | --- |
| Open accumulation | Count blockers in OPEN/ACKNOWLEDGED/MITIGATION/REOPENED |
| Type concentration | Top `blocker_type` counts (WEATHER, MATERIAL, …) |
| Long-lived | `detected_date` age ≥ `OPS_STALL_DAYS` |

**Execution-risk:** HIGH/CRITICAL open blockers deduct up to 30 points from health score (cap applied).

---

## 5. Runtime Anomaly Findings

| Anomaly | Heuristic | Typical false positive |
| --- | --- | --- |
| `concurrency_spike` | ≥2 conflict audits in 7 days | Legitimate concurrent supervisors |
| `duplicate_reporting_spike` | ≥5 report audits in 1 day | 409 retries after refresh |
| `workflow_starvation` | Many PLANNED, no IN_PROGRESS | New project not yet started |
| `inactive_dashboard` | Mutations without overview page views | API-only testing |
| `approval_burst` | ≥4 approvals same day | End-of-week catch-up |

No ML — all rules documented in `operational_intelligence_service.py`.

---

## 6. Project Health Logic

### Score (explainable)

Start at **100**, subtract capped impacts:

| Factor | Max deduction | Trigger |
| --- | --- | --- |
| critical_blockers | 30 | HIGH/CRITICAL open |
| stalled_steps | 25 | Inactivity threshold |
| approval_delays | 20 | Overdue pending |
| inactive_work_orders | 15 | CREATED/ASSIGNED stale |
| reporting_gap | 10 | 0 reports in 7d with WOs present |

### Bands

| Band | Score | Summary tone |
| --- | --- | --- |
| GOOD | ≥75 | Within pilot bounds |
| ATTENTION | 50–74 | Supervisor review needed |
| AT_RISK | <50 | Multiple risk signals |
| UNKNOWN | n/a | DB unavailable |

**Not an AI score** — each deduction listed in `health.components[]` API field.

---

## 7. Predictive Runtime Signals

| Forecast | Confidence | Rule |
| --- | --- | --- |
| `likely_stalled_approval` | high | Already over delay threshold |
| `approval_backlog_risk` | medium | Pending > recent reports |
| `likely_delayed_workflow` | medium | Stalled steps + open blockers |
| `operational_backlog_risk` | low | Many pending approvals, few reports |

Every prediction includes a **reason** string suitable for supervisor standups.

---

## 8. False-Positive Analysis

| Source | Mitigation |
| --- | --- |
| Fixed day thresholds | Tune `OPS_STALL_DAYS`, `OPS_APPROVAL_DELAY_DAYS` per contractor calendar |
| Low data volume | `data_available: false` + UNKNOWN band |
| Pilot seed timestamps | Re-run after fresh pilot week |
| 409 retry spikes | Educate refresh; anomaly is informational |
| Investor reads same signals | Read-only; no extra write paths |

API returns `false_positive_notes[]` for operator training.

### Usefulness criteria (verification)

| Check | Method |
| --- | --- |
| Shape stability | `stage28_verification.py` |
| Supervisor usefulness | Attention list ≤15 items, prioritized critical first |
| Investor clarity | Band + summary without mutation detail overload |

---

## 9. Operational Attention Layer

| Role | UI |
| --- | --- |
| admin, supervisor, investor | Overview → **Operational attention** |
| worker | Hidden (no `canReadRuntime` intelligence need on overview — workers use execution) |

Investors see health band + attention list (read-only). Supervisors see forecasts + expandable signal detail.

**No dashboard redesign** — one `CompactCard` added (Stage 28 scope).

---

## 10. Adoption Risks (Stage 27 → 28)

| Risk | Intelligence response |
| --- | --- |
| Empty JSONL | DB-only signals still work when Postgres up |
| Over-trust in score | Components + false_positive_notes |
| Alert fatigue | Top 5 attention items per category cap |
| Misread predictions | Labelled low/medium/high with explicit reasons |

---

## 11. Artifacts & Verification

| Artifact | Path |
| --- | --- |
| Intelligence service | `backend/phase1/analytics/operational_intelligence_service.py` |
| Schemas | `backend/phase1/schemas/operational_intelligence_schema.py` |
| API | `GET .../operational-intelligence` on analytics router |
| UI | `frontend/components/operational/OperationalAttentionPanel.tsx` |
| Scripts | `stage28_operational_intelligence.py`, `stage28_verification.py` |
| CI | `.github/workflows/stage28-ci.yml` |

```bash
PYTHONPATH=. python backend/scripts/stage28_verification.py
STAGE28_PROJECT_ID=<uuid> PYTHONPATH=. python backend/scripts/stage28_operational_intelligence.py
cd frontend && npm run build
```

### Comparison to Stage 25–27

| Stage | Contribution to Stage 28 |
| --- | --- |
| 25 | Identified approval/report friction — now measured |
| 26 | Faster worker path — should improve reporting_gap signal |
| 27 | JSONL feeds anomaly + inactive dashboard detection |

---

## 12. Recommended Stage 29

1. **Daily health snapshot archive** — Append JSON intelligence summary per project per day.
2. **Supervisor digest email/webhook** — Optional export of `attention_needed` (no new product domain).
3. **Per-step SLA overrides** — Project-level env for thresholds (still heuristic).
4. **OIDC + production pilot** — Required before contractor rollout decisions based on health score.
5. **Calibrate false positives** — One pilot week tuning log for `OPS_*_DAYS`.

---

## Success Criteria (Stage 28)

| Criterion | Met? |
| --- | --- |
| Explainable operational intelligence | Yes — components + reasons |
| Runtime anomaly visibility | Yes — anomalies[] |
| Execution-risk awareness | Yes — health band + blockers |
| Operational forecasting | Yes — predictions[] (heuristic) |
| Meaningful attention signals | Yes — attention panel + API |
| No heavy AI infrastructure | Yes |

---

**Stage 28 complete.** Do not proceed to Stage 29 implementation within this deliverable scope.

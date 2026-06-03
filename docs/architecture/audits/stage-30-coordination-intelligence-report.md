# Stage 30 — Operational Coordination & Team Execution Intelligence Report

**Stage:** 30 — Operational Coordination & Team Execution Intelligence  
**Type:** Explainable coordination heuristics (no autonomous orchestration, no ML)  
**Prerequisites:** Stages 27–29 (telemetry, operational intelligence, decision support)

---

## Executive Summary

Stage 30 adds **team coordination intelligence** on the existing operational-intelligence API: cross-role dependency visibility, execution synchronization signals, handoff-risk detection, communication-gap heuristics, and a lightweight team execution-flow snapshot. Delivery is a **`coordination_intelligence` block** plus an enhanced **Operational attention** overlay — no new orchestration engine and no dashboard redesign.

| Capability | Status |
| --- | --- |
| Coordination bottleneck detection | Implemented |
| Cross-role dependency intelligence | Implemented |
| Execution synchronization visibility | Implemented |
| Supervisor–worker alignment signals | Implemented |
| Handoff-risk intelligence | Implemented |
| Communication-gap heuristics | Implemented |
| Team execution flow metrics | Implemented |
| Coordination attention layer | Overview UI (role-scoped) |
| Verification | `stage30_verification.py`, CI workflow |

---

## 1. Coordination Bottleneck Findings

### Heuristic signals

| Signal | Trigger | Meaning |
| --- | --- | --- |
| `blocked_execution_chain` | Open blocker on IN_PROGRESS / INSPECTION_PENDING / REWORK step | Execution cannot proceed until constraint cleared |
| `approval_coordination_delay` | Pending approvals past `OPS_APPROVAL_DELAY_DAYS` | Supervisor chain slows team |
| (inherits Stage 28) | Stagnation + approval_delays on intel payload | Still visible under stagnation / approval_delays |

### Where coordination fails (typical pilot)

| Failure mode | Observable signal |
| --- | --- |
| Blocker without owner action | `long_lived_blockers` + `blocked_execution_chain` |
| Reports without approvals | `approval_backlog` cross-role dependency |
| Assignments without field feedback | `reporting_handoff` + `incomplete_field_handoff` |

### Design choice

Bottlenecks are **counts + plain-language messages**, not automated rerouting. Supervisors remain the orchestration authority.

---

## 2. Cross-Role Dependency Findings

### Dependency types

| Type | From → To | Detection |
| --- | --- | --- |
| `approval_backlog` | worker → supervisor | pending approvals > reports (7d) |
| `delayed_approval_chain` | supervisor → execution | overdue pending approvals |
| `reporting_handoff` | supervisor → worker | assigned WOs without 7d report |
| `assign_report_gap` | supervisor → worker | assign audits >> reports (informational) |

### Approval dependency chains

Pending approvals are joined to workflow steps and activities. Delayed items feed **coordination_attention** and **handoff_risks** (`approval_handoff_pending` for INSPECTION_PENDING steps).

### Execution waiting states

- Steps with open blockers while not APPROVED.
- Work orders ASSIGNED/IN_PROGRESS with zero reports in 7 days.

---

## 3. Execution Synchronization Findings

| Signal | Logic |
| --- | --- |
| `execution_drift` | Within one activity, step progress spread ≥ 50 points |
| `coordination_fragmentation` | ≥5 PLANNED steps, zero IN_PROGRESS |
| `isolated_stalled_areas` | ≥2 stalled steps clustered per activity code |

### Interpretation

| Pattern | Risk |
| --- | --- |
| Drift | Uneven crew focus inside same activity |
| Fragmentation | Planning done, execution not started |
| Isolated stagnation | One zone starves downstream handoffs |

These are **desynchronization** indicators, not schedule optimization.

---

## 4. Handoff-Risk Analysis

| Handoff type | Severity | Condition |
| --- | --- | --- |
| `blocked_execution_chain` | warning+ | Blocker blocks active step |
| `incomplete_field_handoff` | warning | WO assigned, no 7d report |
| `approval_handoff_pending` | warning | INSPECTION_PENDING + pending approval |

### Ownership ambiguity

BetavanX does not model explicit “owner” UUID on handoffs for pilot users (submitted_by is UUID). Messages reference **work order numbers** and **step codes** to reduce ambiguity without new schema.

### Stale transitions

Covered indirectly via Stage 28 stalled steps and Stage 30 `approval_handoff_pending`.

---

## 5. Communication-Gap Findings

| Signal | Evidence |
| --- | --- |
| `rework_clarification_loop` | REWORK_REQUIRED steps |
| `unresolved_blocker_communication` | Open blockers ≥ stall threshold days |
| `clarification_loop` | ≥2 concurrency conflict audits in 7d |

### Weak coordination areas

- Rework without downstream approval movement.
- Blockers with no resolution date progress.
- High 409 rate (overlap with Stage 26 UX copy).

---

## 6. Team Execution-Flow Findings

### Metrics (`team_execution_flow`)

| Field | Purpose |
| --- | --- |
| `reports_last_7_days` | Field throughput |
| `approvals_last_7_days` | Supervisor throughput (audit proxy) |
| `assignments_last_7_days` | Planning/assign cadence |
| `open_coordination_dependencies` | pending approvals + open blockers + inactive WOs |
| `coordination_density` | open_deps / workflow_step_count |
| `supervisor_responsiveness_ratio` | approvals_7d / max(reports_7d, 1) |

### Coordination band & score

| Band | Score | Summary |
| --- | --- | --- |
| ALIGNED | ≥75 | Handoffs within bounds |
| FRAGMENTED | 50–74 | Review coordination attention |
| STRESSED | <50 | Multiple bottlenecks |

Score deductions are explainable (delayed approvals, blocked chains, report gaps, drift, stale blockers).

---

## 7. Coordination Attention Signals

Unified list (max ~12 items) prioritizing:

1. Handoff risks  
2. Delayed approvals  
3. Critical blockers  
4. Field handoff gaps  
5. Bottleneck summaries  

### UI by role

| Role | Visibility |
| --- | --- |
| admin / supervisor | Full coordination band, team flow, dependencies, handoffs (details) |
| investor | Band + top 4 coordination attention items |
| worker | **worker_relevance** only (2–3 lines) |

---

## 8. False-Positive Analysis

| Scenario | False positive? | Mitigation |
| --- | --- | --- |
| Weather delay | Yes — looks like stagnation | Tune `OPS_STALL_DAYS` |
| End-of-week approval batch | Yes — `approval_burst` / backlog | Notes in `false_positive_notes` |
| New project (all PLANNED) | Yes — `workflow_starvation` / fragmentation | Expect until execution starts |
| Demo seed timestamps | Yes — stale blockers | Fresh pilot week |
| Low audit JSONL volume | Yes — assign/report gap | More pilot usage |

API exposes `false_positive_notes[]` on `coordination_intelligence`. **No autonomous actions** are triggered by signals.

### Attention fatigue risk

- Coordination items capped and ordered by severity.
- Workers see only `worker_relevance` (not full queue).
- Investor view truncated to 4 items.
- Stage 29 priority queue remains separate — supervisors should use priority first, coordination second.

---

## 9. Operational Improvements Applied

| Artifact | Path |
| --- | --- |
| Coordination service | `backend/phase1/analytics/coordination_intelligence_service.py` |
| Schema | `OperationalCoordinationIntelligenceRead` in `operational_intelligence_schema.py` |
| API | `coordination_intelligence` on `GET .../operational-intelligence` |
| UI | `OperationalAttentionPanel.tsx` coordination sections |
| Types | `frontend/lib/api/phase1/intelligence.ts` |
| Role policy | `canViewCoordinationDetail()` |
| Scripts | `stage30_verification.py`, `stage30_coordination_intelligence.py` |
| CI | `.github/workflows/stage30-ci.yml` |

---

## 10. Verification

```bash
PYTHONPATH=. python backend/scripts/stage30_verification.py
STAGE30_PROJECT_ID=<uuid> PYTHONPATH=. python backend/scripts/stage30_coordination_intelligence.py
cd frontend && npm run build
```

### Comparison to Stages 27–29

| Stage | Stage 30 builds on |
| --- | --- |
| 27 | Audit JSONL for assign/approve/report/conflict rates |
| 28 | Health, stagnation, blockers, predictions |
| 29 | Priority queue — coordination does not replace it |

---

## 11. Recommended Stage 31

1. **Daily coordination snapshot archive** — JSONL per project per day for trend lines.  
2. **Per-activity SLA overrides** — Optional env per project code (still heuristic).  
3. **Supervisor digest** — Export top coordination_attention + priority_queue #1–3.  
4. **Activity deep-link** — Link coordination items to `activity-instances/[id]` when resolvable.  
5. **Calibrate on live pilot** — Record false-positive rate weekly from supervisor feedback.

---

## Success Criteria (Stage 30)

| Criterion | Met? |
| --- | --- |
| Explainable coordination intelligence | Yes |
| Execution synchronization visibility | Yes |
| Meaningful coordination-risk awareness | Yes |
| Actionable handoff visibility | Yes |
| Operationally useful team-level intelligence | Yes (metrics + band) |
| No autonomous orchestration | Yes |

---

**Stage 30 complete.** Do not proceed to Stage 31 implementation within this deliverable scope.

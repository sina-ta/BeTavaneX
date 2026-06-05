# COSC — Execution Physics Semantic Extraction

> What dimensions of **real construction execution** the BetavanX runtime actually
> represents, weakly represents, or doesn't represent at all — and where its
> simplifications are dangerous. Semantic analysis only: no runtime changes, no new
> entities, no simulation, no optimization, no AI.
>
> Reference frame: "execution physics" here means the real behavior of building
> work — how work proceeds, at what rate, under what constraints, with what
> variability, and how disturbances propagate. The question is how much of that
> physics the current data model and services can express.

## The one-paragraph truth

BetavanX models execution as **discrete commitments that flip from incomplete to
complete**, rolled up by **unweighted averaging**, gated by a **convention-based
status machine**, and observed by **heuristics over audit logs**. It records a lot
of execution *facts* (dates, counts, statuses, weights) but reasons about almost
none of them as *physics*. There is no notion of rate, duration behavior,
contention, variability, or propagation. The philosophy doc
(`core-operational-decisions.md`) describes a far richer execution reality
(multi-factor readiness, confidence-aware truth) that the runtime does **not**
implement. This gap is the subject of this document.

### Representation scorecard

| Execution dimension | State |
|---|---|
| Work decomposition (what/where) | **Modeled** |
| Commitment → completion progress | **Modeled (coarse)** |
| Governance gating | **Modeled (partial)** |
| Coordination linkage | **Modeled (link) / Observed (friction)** |
| Quality / rework loop | **Modeled (recorded), no propagation** |
| Temporal data (planned/actual) | **Recorded, inert** |
| Resource demand/contention | **Weak (descriptive only)** |
| Execution variability / uncertainty | **Weak (heuristic labels only)** |
| Delay propagation | **Weak (observed, no cascade)** |
| Blocker impact | **Weak (inert)** |
| Production rate / throughput | **Absent** |
| Spatial congestion / trade stacking | **Absent** |
| Productivity degradation | **Absent** |
| Schedule network (predecessors/float) | **Absent** |
| Earned value / cost actuals | **Absent** |
| Uncertainty accumulation / entropy | **Absent** |

---

## 1. Current Execution Representation

What the runtime genuinely models.

### 1.1 Discrete work decomposition (the spatial-structural unit)
Execution is located at the `WorkflowStep`, which belongs to an `ActivityInstance`
= the unique intersection of `WBSItem` (*what*) × `Location` (*where*). This is a
real, enforced decomposition (`activity-instances` unique on
`(project_id, wbs_item_id, location_id)`). The atom of execution is the step.

### 1.2 Commitment-based progress (the only real "motion" model)
The runtime's physics of progress is:

> Field work is committed via `WorkOrder`s; each commitment carries an
> `execution_weight` (`WorkOrderWorkflowStep`); when a work order reaches
> `COMPLETED`, its weight counts as done.

`ProgressService`: `step% = Σ(completed weight) / Σ(all weight) × 100`, then
**unweighted means** up to activity and project. This is a genuine commitment →
completion model — coarse, but it is the system's one expression of execution
advancing.

### 1.3 Governance gating (execution authority transitions)
`WorkflowStep` has a status machine; `WorkflowGovernanceService` performs
inspection-pass (guarded on `INSPECTION_PENDING`), inspection-fail, rework, and
approval (with duplicate-approval protection). This models the **acceptance**
physics of execution — work isn't just done, it's validated. (Consistent with
philosophy axiom #3: approval validates, it doesn't create reality.)

### 1.4 Coordination linkage (who is committed to what)
The `WorkOrder ↔ WorkflowStep` assignment is the unit of field coordination, and
`DailyReport` is the evidence a committed work order produced output. This is real
coordination *structure*.

### 1.5 Constraint registration and quality loop
`Blocker` (type/severity/lifecycle) records impediments; `Inspection` →
`result PASS/FAIL` → `PunchItem` records the quality/remediation loop;
`REWORK_REQUIRED` records reopened execution. These are recorded faithfully.

### 1.6 Operational lineage
The new event ledger (`event-ledger-foundation.md`) records *that* assignment,
reporting, approval, and blocker events happened, with actor and time — the raw
substrate any future timing analysis would need.

**Summary:** the runtime models execution **as discrete states and commitments**.
That is legitimate and useful. What it does not model is execution as a *process
with rates, durations, and interactions* — see below.

---

## 2. Weakly Modeled Execution Dynamics

Present in the data, but too shallow to reason about. (Data exists; physics does
not.)

### 2.1 Resource demand — descriptive, never reconciled
`WorkflowStepTemplate.required_resources / required_permits / required_documents`
(JSONB) and `DailyReport.reported_manpower / reported_equipment /
reported_material_entries` exist. But:
- requirements are free-form reference text/JSON, never matched against anything;
- reported counts are raw numbers, never aggregated into utilization or rate;
- there is **no availability, capacity, or contention** concept.
So "resource" is a label, not a constraint (see `dependency-taxonomy.md`:
`resource_dependency` = Declared/descriptive).

### 2.2 Temporal behavior — recorded, inert
`WorkflowStep.planned_start/finish/actual_start/actual_finish`,
`ActivityInstance.planned_start/finish/planned_duration_days`,
`WorkOrder.planned_date`, blocker `detected_date/resolved_date` all exist. **None
drive any computation.** `planned_duration_days` is stored and never used; planned
vs actual is never reconciled into variance. The system knows *when* things were
planned/happened but computes nothing from it except analytics' `updated_at`-age
staleness heuristics.

### 2.3 Execution variability — only as heuristic labels
`decision_support_service` emits `confidence: high/medium/low` and `priority_score`
values; analytics carry `false_positive_notes`. These are **deterministic
threshold outputs dressed as confidence** — there is no variance, distribution, or
probabilistic basis. Variability is named, not modeled.

### 2.4 Delay & disturbance — observed, never propagated
Stalls, long-lived blockers, delayed approvals are detected by `updated_at` age vs
`OPS_STALL_DAYS`/`OPS_APPROVAL_DELAY_DAYS`. But a delay on one step **does not
propagate** to anything downstream, because there are no downstream edges (no
predecessors). Delay is a per-row observation, not a network effect.

### 2.5 Coordination friction — inferred from audit keywords
`coordination_intelligence_service` infers handoff risk, approval-vs-reporting
imbalance, assign/report gaps — by **counting substrings** in audit JSONL
(`"approve"`, `"submit"`, `"assign"`). It's a real attempt at friction modeling but
rests on log text, not on modeled coordination state.

### 2.6 Rework — a status, not a consequence
`REWORK_REQUIRED` exists and is flagged by analytics, but rework **does not
invalidate prior approvals, does not reset progress, does not cascade** to
dependent work. The loop is recorded; its physics (rework ripples backward and
forward) is absent.

### 2.7 Blocker impact — inert
`Blocker.severity` up to `CRITICAL` changes **nothing** in execution: a step can be
approved and driven to 100% with an open CRITICAL blocker. Blockers affect only
analytics scores (fragility F9). The single most important execution-physics
concept — "work is stopped" — has no operational effect.

---

## 3. Missing Execution Reality Dimensions

No representation at all. These are the parts of construction physics the model
cannot currently express.

### 3.1 Production rates & crew throughput
There is no crew/labor entity, no output-per-unit-time, no "m³/day" or
"units/shift." `DailyReport` counts heads and equipment but never derives a rate.
Without rates, **finish dates cannot be forecast** from execution behavior — only
guessed from calendar fields.

### 3.2 Schedule network (predecessors, successors, float, critical path)
This is the biggest gap. There are **no inter-step or inter-activity sequencing
relationships anywhere in the data model.** Sequencing exists only as a social
convention over statuses (`lifecycle-semantics.md`) and containment. Therefore:
critical path, float, dependency-driven delay propagation, and "what unblocks what"
are all impossible to express today.

### 3.3 Spatial congestion / trade stacking
`Location` is pure classification. There is no concept of multiple activities
competing for the same space at the same time, no occupancy limit, no trade-stacking
penalty. Real sites lose productivity to congestion; the model can't see it.

### 3.4 Productivity degradation
No fatigue, learning curve, overtime decay, or weather-driven productivity loss.
Output is implicitly assumed constant and binary (committed → done).

### 3.5 Partial / continuous completion
A `WorkOrder` contributes its weight **only when fully `COMPLETED`** — there is no
partial work-order progress. Real daily output is continuous; the model quantizes
it to 0/100 per commitment. A step with weeks of real partial work reads 0% until a
work order flips.

### 3.6 Earned value & cost actuals
`BOQItem`/`BOQMapping` hold **planned** quantity/cost only. No actual cost, no
earned value, no cost/schedule variance. Financial execution physics is absent.

### 3.7 Environmental dynamics
Weather appears only as a discrete `Blocker` type and free-text
`DailyReport.weather_notes`. There is no continuous environmental factor affecting
rates or readiness.

### 3.8 Uncertainty accumulation / execution entropy
No probabilistic state, no variance that compounds along a chain, no confidence that
degrades with distance from evidence. The philosophy's "confidence-aware truth"
(axiom #1) has no runtime substrate.

---

## 4. Unrealistic Runtime Assumptions

Where the current simplifications actively misrepresent reality.

1. **Progress is an unweighted average of binary commitments.** A 2-hour step and a
   3-month step count equally toward an activity; a work order is 0% or 100% of its
   weight. Project % can move on trivial completions and ignore massive in-progress
   work. `planned_weight` exists but is unused. This is the most consequential
   unrealistic assumption — the headline number is often meaningless.
2. **Readiness is a single unowned boolean.** The philosophy (axiom #2) defines
   readiness as predecessors + constraints + governance + resources + spatial
   access + coordination. The runtime has `WorkflowStep.ready: bool` that **nothing
   computes** (fragility F8). Binary, static, and disconnected from every factor it
   supposedly represents.
3. **Completion is deterministic and instantaneous.** Status is a discrete flip with
   no "likely to slip," no duration, no in-flight uncertainty. Execution is treated
   as a sequence of atomic events, not a process.
4. **Activities and steps are independent.** Roll-ups average children as if
   unrelated. Real execution is a dependency network where one slip cascades — the
   model has no edges to cascade along.
5. **Time is decorative.** Planned and actual dates coexist but are never
   reconciled; durations never drive anything. The system looks schedule-aware and
   is not.
6. **Constraints are advisory.** Blockers, resource requirements, and permits read
   like gates but enforce nothing. The model implies control it does not exert.
7. **One activity per WBS×Location.** Assumes a clean, non-iterative decomposition;
   real work is overlapping and repeated (multiple pours, re-work cycles, phased
   handovers).

---

## 5. Future Operational Physics Requirements

Which future intelligence layers are **blocked** until the physics substrate
matures. (Stated as dependencies, not as a build plan.)

| Future layer | Requires execution physics that today is… |
|---|---|
| **Finish-date forecasting** | production rates + durations + schedule network — **absent** |
| **Operational simulation** | rates + resource/capacity + congestion + stochastic durations — **absent** |
| **Delay/impact propagation** | predecessor/successor edges + propagation rules — **absent** |
| **Coordination intelligence (mature)** | modeled coordination state + handoff timing (not audit-keyword counting) — **weak** |
| **Dependency propagation** | the dependency graph substrate (`dependency-taxonomy.md` §6) — **absent** |
| **Execution prediction / risk** | variability + uncertainty accumulation + confidence physics — **absent** |
| **AI reasoning over execution** | confidence-aware lineage (ledger is a start) + all of the above — **mostly absent** |

The blunt consequence: **every "smart" feature on the roadmap currently has to be
faked**, because the execution-physics inputs (rate, duration, dependency,
variance) don't exist. The existing analytics already demonstrate this — they are
honest heuristics over logs precisely because there is no physics to compute on.

---

## 6. Architectural Risk Areas

1. **Progress-as-truth risk (high).** If the unweighted/binary/uncached progress
   number drives decisions, payments, or reporting, it will mislead. It is currently
   the most visible and least trustworthy execution metric (combine with fragility
   F2/F3/F20).
2. **Confidence theater (high).** Emitting `confidence: high/medium/low` and
   priority scores with no probabilistic basis lends false authority. Consumers (and
   future AI) will over-trust deterministic thresholds.
3. **No dependency network (high).** Any future scheduling/forecasting/propagation
   feature has no substrate; building one on convention-only sequencing would
   institutionalize the fragility.
4. **Inert constraints (safety risk).** A CRITICAL blocker that doesn't stop
   approval is an operational and safety hazard if users assume blockers gate work.
5. **Decorative time (medium).** Schedule-looking fields that compute nothing invite
   features built on inert data.
6. **Descriptive resources (medium).** Resource-based recommendations would be
   unfounded; the data implies capacity awareness that doesn't exist.
7. **Philosophy/runtime divergence (medium).** `core-operational-decisions.md`
   asserts execution semantics (multi-factor readiness, confidence-aware,
   reconcilable truth) the runtime doesn't model. Future work that trusts the axioms
   as implemented will be wrong.

---

## 7. Recommendations for Semantic Stabilization

Semantic, not constructional. The theme: **stop implying physics you don't model;
define the missing dimensions before anyone builds on them.**

1. **Label derived values for what they are.** Progress = "commitment-completion
   coverage (unweighted)," readiness = "manual hint," confidence = "rule-based
   label." Put this in the API/contract semantics so consumers and future models
   don't over-trust. (No behavior change.)
2. **Name the missing execution unit dimensions explicitly.** Before any table:
   define, in COSC terms, *duration behavior*, *partial completion*, *production
   rate*, *predecessor relation*, and *resource demand* as first-class operational
   concepts that the model currently lacks. Definition first, structure later.
3. **Treat the dependency network as the prerequisite substrate.** Adopt
   `dependency-taxonomy.md` §6 as the gate: no forecasting/propagation semantics
   until sequencing edges and same-aggregate invariants exist as *concepts*.
4. **Use the event ledger to capture real execution timing.** "started/completed"
   lineage (occurred_at) is the honest raw material for future rate/variance —
   captured passively, without building simulation. Recommend recording execution
   *transitions* as events when those operations exist, so timing history accrues.
5. **Reconcile the three definitions of "done"** (`COMPLETED` vs `APPROVED` vs
   `progress=100`, fragility F16) — forecasting and EVM are impossible while "done"
   is ambiguous.
6. **Decide blocker authority.** Either document blockers as advisory (and stop
   implying they gate) or define (semantically) that open CRITICAL blockers
   constrain readiness/approval. Pick one; the current ambiguity is the most
   dangerous physics gap.
7. **Define readiness as a derived, multi-factor state** matching philosophy axiom
   #2 — even if only documented now — so the unowned `ready` boolean stops standing
   in for a concept it cannot carry.
8. **Keep philosophy and runtime honestly aligned.** Annotate
   `core-operational-decisions.md` axioms with their current implementation status
   (implemented / partial / aspirational) so the COSC stays truthful about what is
   real today.

---

## 8. Bottom line

BetavanX has a solid **state-and-commitment** model of execution and an honest
analytics layer that interprets it. What it lacks is **process physics**: rates,
durations, dependencies, contention, variability, and propagation. Most of the
"execution reality" a construction platform eventually needs is either inert data
(time, resources, blockers) or entirely absent (rates, congestion, schedule
network, uncertainty). The runtime's simplifications are acceptable for a pilot but
become misleading the moment progress, readiness, or confidence are trusted as
physical truth. The path forward is not simulation or AI — it is to **define the
missing execution dimensions semantically and stop the data model from implying a
physics it does not compute.**

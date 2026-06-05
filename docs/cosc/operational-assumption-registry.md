# COSC — Operational Assumption Registry

> The single, honest list of what the BetavanX runtime currently **assumes,
> simplifies, or fakes**. Its purpose is architectural self-awareness: to prevent
> the platform from treating its current semantics as more mature than they are.
>
> This is **documentation only**. No runtime changes, no new systems, no scheduling
> engine, no graph DB, no simulation, no AI. Every assumption below is grounded in
> code that exists today; nothing here is hypothetical.

## How to read this

Each assumption is rated on **Architectural Severity** using one scale:

- **Acceptable** — a reasonable simplification for the Early Semantic Runtime Phase;
  safe as long as it stays labeled and nobody builds physics on it.
- **Fragile** — works by convention; breaks silently under load, concurrency, or
  edge cases. Needs guardrails.
- **Dangerous** — actively misleads consumers or decisions if trusted as truth.
- **Critical** — can cause operational/safety harm or institutionalize a flaw that
  later layers cannot undo.

Cross-references: `semantic-fragility-audit.md` (F#), `dependency-taxonomy.md`,
`execution-physics.md`, `lifecycle-semantics.md`, `operational-boundaries.md`,
`core-operational-decisions.md` (axioms).

---

## 1. Runtime Assumption Matrix

| # | Assumption | Type | Severity | Acceptable / Fragile / Dangerous / Critical |
|---|---|---|---|---|
| A1 | Progress = unweighted average of children | Semantic simplification | High | **Dangerous** |
| A2 | Work order contributes 0% or 100% (no partial) | Semantic simplification | High | **Dangerous** |
| A3 | `progress_percent` is a stored cache treated as live | Stale-truth shortcut | High | **Dangerous** |
| A4 | `ready` is a single, unowned boolean | Weak abstraction | Medium | **Fragile** |
| A5 | Blockers do not propagate / do not gate | Non-propagating semantics | High | **Critical** |
| A6 | Time fields are decorative (planned vs actual never reconciled) | Inert data | Medium | **Fragile** |
| A7 | Child execution is independent (roll-up by mean) | Semantic simplification | Medium | **Fragile** |
| A8 | No production-rate / throughput model | Missing physics | Medium | **Acceptable** (blocks forecasting) |
| A9 | No delay propagation | Non-propagating semantics | Medium | **Fragile** |
| A10 | No uncertainty / confidence physics | Missing physics | Low | **Acceptable** |
| A11 | No real dependency network (sequencing = convention) | Missing physics | High | **Dangerous** |
| A12 | Coordination intelligence = audit-keyword heuristics | Weak abstraction | Medium | **Acceptable** (if labeled) |
| A13 | Analytics are advisory-only (observe, never control) | By-design boundary | Low | **Acceptable** |
| A14 | Completion is deterministic & instantaneous | Semantic simplification | Medium | **Fragile** |
| A15 | Governance gates without checking execution reality | Governance-without-physics | High | **Dangerous** |
| A16 | Status ordering enforced by convention, not architecture | Semantic shortcut | Medium | **Fragile** |
| A17 | Three different definitions of "done" coexist | Semantic duplication | High | **Dangerous** |
| A18 | Client-supplied attribution / weights are trusted | Trust shortcut | Medium | **Fragile** |
| A19 | Resource requirements/reports are descriptive only | Inert data | Low | **Acceptable** |
| A20 | One activity per WBS×Location (no iterative/overlapping work) | Structural simplification | Low | **Acceptable** |

---

## 2. Detailed Assumptions

Each entry: **Current Runtime Behavior · Simplification Type · Reality Gap ·
Operational Risk · Architectural Severity · Future Dependency Impact · Recommended
Stabilization · Classification.**

### A1 — Progress is an unweighted average of children
- **Current behavior:** `ProgressService` computes step% from completed work-order
  weight, then takes a plain mean up to activity and project. `planned_weight`
  exists on the model but is **not used**.
- **Simplification type:** semantic simplification (equal weighting).
- **Reality gap:** a 2-hour task and a 3-month task count equally. Real progress is
  weighted by effort/value.
- **Operational risk:** headline progress moves on trivial work and ignores large
  in-progress work; misleads reporting and any payment/decision tied to it.
- **Architectural severity:** High.
- **Future dependency impact:** forecasting, earned value, and any KPI that trusts
  progress inherit the distortion.
- **Recommended stabilization:** define weighted roll-up semantics (use existing
  `planned_weight`); until then, label the metric as "unweighted coverage."
- **Classification:** Dangerous. (F2)

### A2 — Work orders contribute 0% or 100%
- **Current behavior:** a work order's `execution_weight` counts only when its
  status is `COMPLETED`; there is no partial contribution.
- **Simplification type:** binary quantization of continuous output.
- **Reality gap:** field work is continuous; daily output is partial. A step under
  weeks of real work reads 0% until a work order flips.
- **Operational risk:** progress lags reality badly; "stuck at 0%" steps that are
  actually advancing; demoralizing and misleading.
- **Architectural severity:** High.
- **Future dependency impact:** throughput, rate, and forecasting can't be derived
  from binary commitments.
- **Recommended stabilization:** define partial-completion semantics for work orders
  (concept first, structure later).
- **Classification:** Dangerous.

### A3 — `progress_percent` is a cache treated as truth
- **Current behavior:** progress is stored on the row and read back; recomputation
  is not guaranteed on every dependency change, so the stored value can be stale.
- **Simplification type:** derived-truth caching without invalidation contract.
- **Reality gap:** a cache without an invalidation rule is not truth; it's a
  snapshot of unknown age.
- **Operational risk:** different screens/queries can disagree; decisions made on
  stale numbers.
- **Architectural severity:** High.
- **Future dependency impact:** any consumer that trusts the field (analytics,
  exports, forecasting) propagates the staleness.
- **Recommended stabilization:** define whether progress is derived-on-read or
  cached-with-invalidation, and document it as a truth contract.
- **Classification:** Dangerous. (F2/F3/F20, `truth-contracts.md`)

### A4 — `ready` is a single, unowned boolean
- **Current behavior:** `WorkflowStep.ready: bool` exists; **nothing computes it**;
  no service owns it.
- **Simplification type:** weak abstraction collapsing a multi-factor state into one
  flag.
- **Reality gap:** philosophy axiom #2 defines readiness as predecessors +
  constraints + governance + resources + spatial access + coordination. A boolean
  carries none of that.
- **Operational risk:** "ready" means whatever someone last set it to; false
  go-signals.
- **Architectural severity:** Medium.
- **Future dependency impact:** readiness-driven scheduling, coordination, and
  dispatch are impossible while readiness is opaque.
- **Recommended stabilization:** define readiness as a derived, multi-factor state
  (documented now, computed later); assign ownership.
- **Classification:** Fragile. (F8)

### A5 — Blockers do not propagate and do not gate
- **Current behavior:** `Blocker` records type/severity/lifecycle; severity up to
  `CRITICAL` changes nothing. A step with an open CRITICAL blocker can still be
  approved and driven to 100%. Blockers affect only analytics scores.
- **Simplification type:** non-propagating, non-enforcing semantics.
- **Reality gap:** "work is blocked" is the most basic execution-physics fact; here
  it is inert.
- **Operational risk:** operational and **safety** risk if users assume blockers
  stop work; governance proceeds over unsafe/blocked conditions.
- **Architectural severity:** High.
- **Future dependency impact:** delay propagation, readiness, and risk all need
  blocker impact to mean something.
- **Recommended stabilization:** decide blocker authority — advisory vs gating — and
  document it explicitly. This is the most urgent semantic decision.
- **Classification:** Critical. (F9)

### A6 — Time semantics are decorative
- **Current behavior:** `planned_start/finish`, `actual_start/finish`,
  `planned_duration_days`, `planned_date` are stored; **none drive computation**.
  Planned vs actual is never reconciled; `planned_duration_days` is unused.
- **Simplification type:** inert data (schedule-looking, schedule-unaware).
- **Reality gap:** time is the backbone of execution; here it's metadata.
- **Operational risk:** the system appears schedule-aware and is not; features built
  on these fields would compute on inert data.
- **Architectural severity:** Medium.
- **Future dependency impact:** forecasting, variance, critical path all need time
  to be reasoned about, not just stored.
- **Recommended stabilization:** define variance/duration semantics, or explicitly
  mark these fields as record-only.
- **Classification:** Fragile.

### A7 — Child execution is independent
- **Current behavior:** roll-ups average children with no relationships between them.
- **Simplification type:** independence assumption.
- **Reality gap:** real execution is a network; one slip cascades. There are no
  edges to cascade along.
- **Operational risk:** aggregate states hide coupled failures; "everything's 70%"
  while a blocking item stalls the rest.
- **Architectural severity:** Medium.
- **Future dependency impact:** propagation, critical path, and impact analysis are
  impossible without modeled inter-child relationships.
- **Recommended stabilization:** treat the dependency network (A11) as the
  prerequisite; document independence as a known false assumption.
- **Classification:** Fragile.

### A8 — No production-rate / throughput model
- **Current behavior:** `DailyReport` counts manpower/equipment/material as raw
  numbers; no output-per-time is derived; no crew/labor entity exists.
- **Simplification type:** missing execution physics.
- **Reality gap:** without rates, finish dates can't be forecast from behavior.
- **Operational risk:** none today (nothing claims throughput); risk is *future*
  features faking it.
- **Architectural severity:** Medium (latent).
- **Future dependency impact:** forecasting and simulation are blocked entirely.
- **Recommended stabilization:** define "production rate" and "throughput" as
  concepts; use the event ledger to accrue real timing as raw material.
- **Classification:** Acceptable (now) — but a hard blocker for forecasting.

### A9 — No delay propagation
- **Current behavior:** stalls/long-lived blockers/delayed approvals are detected
  per-row by `updated_at` age; a delay never propagates downstream.
- **Simplification type:** non-propagating semantics.
- **Reality gap:** delays cascade in reality; here each is an isolated observation.
- **Operational risk:** downstream impact invisible; surprises late.
- **Architectural severity:** Medium.
- **Future dependency impact:** depends on A11 (no edges to propagate along).
- **Recommended stabilization:** gate on dependency network; document as observed,
  not propagated.
- **Classification:** Fragile.

### A10 — No uncertainty / confidence physics
- **Current behavior:** `decision_support` emits `confidence: high/medium/low` from
  deterministic thresholds; no variance or distribution exists.
- **Simplification type:** missing physics (confidence is a label, not a measure).
- **Reality gap:** philosophy axiom #1 demands confidence-aware truth; there is no
  substrate.
- **Operational risk:** **confidence theater** — false authority if trusted.
- **Architectural severity:** Low (today) / High (if trusted).
- **Future dependency impact:** AI reasoning and risk scoring need real uncertainty.
- **Recommended stabilization:** label confidence outputs as "rule-based," not
  probabilistic.
- **Classification:** Acceptable (if honestly labeled).

### A11 — No real dependency network
- **Current behavior:** there are **no predecessor/successor edges** anywhere.
  Sequencing exists only as containment + status convention.
- **Simplification type:** missing physics (the foundational gap).
- **Reality gap:** construction is fundamentally a dependency network; the model
  cannot express "X must precede Y."
- **Operational risk:** critical path, float, propagation, and truthful forecasting
  are all impossible; any such feature must be faked.
- **Architectural severity:** High.
- **Future dependency impact:** **the** prerequisite substrate for nearly every
  future intelligence layer (`dependency-taxonomy.md` §6).
- **Recommended stabilization:** adopt the dependency-taxonomy graph-readiness as a
  gate: no propagation/forecasting semantics until edges exist as concepts.
- **Classification:** Dangerous (foundational).

### A12 — Coordination intelligence from audit keywords
- **Current behavior:** `coordination_intelligence_service` infers handoff risk and
  imbalances by counting substrings (`"approve"`, `"submit"`, `"assign"`) in audit
  JSONL.
- **Simplification type:** weak abstraction (log text as signal).
- **Reality gap:** coordination friction is structural; keyword counts are a proxy.
- **Operational risk:** brittle to log-format changes; false signals.
- **Architectural severity:** Medium.
- **Future dependency impact:** mature coordination intelligence needs modeled
  coordination state, not log mining.
- **Recommended stabilization:** keep, but label as heuristic; migrate signal source
  to the event ledger over time.
- **Classification:** Acceptable (if labeled).

### A13 — Analytics are advisory-only
- **Current behavior:** analytics observe and recommend; they never mutate execution
  state (`operational-boundaries.md`).
- **Simplification type:** intentional boundary (not a flaw).
- **Reality gap:** none — this is a correct, honest design choice.
- **Operational risk:** only if a future layer wires analytics into control without
  revisiting the boundary.
- **Architectural severity:** Low.
- **Future dependency impact:** any closed-loop feature must explicitly cross this
  boundary deliberately.
- **Recommended stabilization:** keep the boundary explicit; document it as a
  contract.
- **Classification:** Acceptable (by design).

### A14 — Completion is deterministic and instantaneous
- **Current behavior:** status is a discrete flip; no "likely to slip," no duration,
  no in-flight probability.
- **Simplification type:** semantic simplification (process modeled as events).
- **Reality gap:** completion is a process with duration and risk, not an instant.
- **Operational risk:** no early-warning signal from execution itself.
- **Architectural severity:** Medium.
- **Future dependency impact:** prediction/risk need in-flight, probabilistic state.
- **Recommended stabilization:** define execution-in-progress semantics; use ledger
  timing to observe real durations.
- **Classification:** Fragile.

### A15 — Governance gates without checking execution reality
- **Current behavior:** approval/inspection transitions enforce status guards and
  duplicate-approval protection, but do **not** check resources, blockers,
  readiness, or predecessors.
- **Simplification type:** governance-without-physics.
- **Reality gap:** approving work says nothing about whether it was physically
  possible/safe; governance floats above execution.
- **Operational risk:** formally-approved work over open blockers/unmet constraints;
  governance gives false assurance.
- **Architectural severity:** High.
- **Future dependency impact:** trustworthy governance needs readiness (A4) and
  blocker authority (A5) to mean something.
- **Recommended stabilization:** define which execution constraints governance must
  consult (semantically), aligned with axioms #2/#3.
- **Classification:** Dangerous.

### A16 — Status ordering is convention, not architecture
- **Current behavior:** valid lifecycle orderings are enforced socially and by a few
  guards, not by a complete state machine (`lifecycle-semantics.md`).
- **Simplification type:** semantic shortcut.
- **Reality gap:** invalid transitions are reachable through weak enforcement.
- **Operational risk:** inconsistent lifecycle states; data that violates intended
  ordering.
- **Architectural severity:** Medium.
- **Future dependency impact:** any reasoning over lifecycle assumes orderings the
  runtime doesn't guarantee.
- **Recommended stabilization:** define the canonical state machine (documented now,
  enforced later).
- **Classification:** Fragile. (F1)

### A17 — Three coexisting definitions of "done"
- **Current behavior:** `WorkOrder.COMPLETED`, `WorkflowStep.APPROVED`, and
  `progress = 100` can each independently signal "done" and need not agree.
- **Simplification type:** semantic duplication.
- **Reality gap:** "done" should be one reconcilable concept.
- **Operational risk:** different layers report different completion; reconciliation
  impossible.
- **Architectural severity:** High.
- **Future dependency impact:** forecasting and earned value require an
  unambiguous "done."
- **Recommended stabilization:** define the authoritative completion concept and how
  the three relate.
- **Classification:** Dangerous. (F16)

### A18 — Client-supplied attribution and weights are trusted
- **Current behavior:** some attribution fields and `execution_weight` originate from
  client input and are persisted without independent derivation.
- **Simplification type:** trust shortcut.
- **Reality gap:** authoritative operational facts should be server-derived or
  validated.
- **Operational risk:** progress/attribution manipulable by input; lineage less
  trustworthy.
- **Architectural severity:** Medium.
- **Future dependency impact:** trustworthy lineage and metrics need validated
  inputs.
- **Recommended stabilization:** define which fields are authoritative vs declared;
  validate authoritative ones.
- **Classification:** Fragile.

### A19 — Resource data is descriptive only
- **Current behavior:** `required_resources/permits/documents` and reported counts
  are free-form/raw; never matched to availability or capacity.
- **Simplification type:** inert data.
- **Reality gap:** resources constrain execution; here they're labels.
- **Operational risk:** none today; risk is future resource features built on
  descriptive data.
- **Architectural severity:** Low.
- **Future dependency impact:** resource leveling/contention needs a real resource
  model.
- **Recommended stabilization:** define resource demand/availability as concepts
  before any resource-based feature.
- **Classification:** Acceptable (now).

### A20 — One activity per WBS×Location
- **Current behavior:** `ActivityInstance` is unique on
  `(project_id, wbs_item_id, location_id)`.
- **Simplification type:** structural simplification.
- **Reality gap:** real work is iterative/overlapping (multiple pours, phased
  handovers, rework cycles).
- **Operational risk:** low now; constrains modeling of repeated/phased work.
- **Architectural severity:** Low.
- **Future dependency impact:** iterative execution modeling would need to revisit
  uniqueness.
- **Recommended stabilization:** document the constraint and its limits; revisit only
  if iterative work becomes a requirement.
- **Classification:** Acceptable.

---

## 3. Semantic Simplifications (summary)

The runtime collapses several continuous, networked realities into discrete,
independent values: **unweighted averaging (A1)**, **binary commitment (A2)**,
**independent children (A7)**, **deterministic completion (A14)**, and
**convention-based ordering (A16)**. Individually defensible for a pilot; together
they mean the system's aggregate numbers describe a simpler world than the one on
site.

## 4. Missing Execution Physics (summary)

No rate/throughput (A8), no dependency network (A11), no delay propagation (A9), no
uncertainty (A10). These are not bugs — they are absent dimensions. The key honesty
point: **every future intelligence feature depends on at least one of these, so
none can be built truthfully yet.** See `execution-physics.md` §5.

## 5. Temporary Architectural Compromises

These are shortcuts taken for speed that should be explicitly time-boxed in
intent:

- **A3** progress cache without invalidation contract.
- **A12** coordination signal mined from audit-log text rather than the event
  ledger.
- **A18** trusting client-supplied attribution/weights.
- **A4** `ready` boolean standing in for a multi-factor concept.

Each is fine *as a labeled compromise* and harmful *as an unmarked truth*.

## 6. Assumption Severity Map

| Severity | Assumptions |
|---|---|
| **Critical** | A5 (non-gating blockers — safety) |
| **Dangerous** | A1, A2, A3, A11, A15, A17 |
| **Fragile** | A4, A6, A7, A9, A14, A16, A18 |
| **Acceptable** | A8, A10, A12, A13, A19, A20 |

Read it as: one safety-class item (A5), a cluster of "truth-misleading" items
(progress family A1–A3, plus A11/A15/A17), a band of convention-fragile items, and a
floor of honest early-phase simplifications.

## 7. Future Architectural Pressure Areas

Where these assumptions will first break as the platform grows:

1. **The progress family (A1/A2/A3)** — the moment progress drives money,
   reporting, or client-facing dashboards.
2. **The dependency vacuum (A11/A7/A9)** — the moment anyone asks "what's the
   critical path?" or "what does this delay affect?"
3. **Governance/blocker honesty (A5/A15)** — the moment a blocked or unsafe item is
   formally approved and someone notices.
4. **Completion ambiguity (A17)** — the moment two reports of "% done" disagree.
5. **Confidence theater (A10)** — the moment a "high confidence" recommendation is
   wrong and trusted.

## 8. Recommended Stabilization Priorities

Ordered by risk-reduction per effort. **All are semantic/documentation steps — none
require building the missing systems now.**

1. **Decide blocker authority (A5).** Advisory or gating — pick and document. Highest
   risk, lowest effort. (Safety.)
2. **Label the progress family honestly (A1/A2/A3).** State in the contract that
   progress is unweighted, binary-sourced, and possibly cached. Stop it being read as
   physical truth.
3. **Reconcile "done" (A17).** Define the authoritative completion concept and how
   `COMPLETED`/`APPROVED`/`100%` relate.
4. **Define readiness as multi-factor (A4)** and **governance's required checks
   (A15)** — align documentation with axioms #2/#3.
5. **Establish the dependency network as the prerequisite gate (A11).** No
   propagation/forecasting semantics until edges exist as concepts.
6. **Mark inert/heuristic surfaces (A6/A10/A12/A18/A19)** as record-only or
   heuristic so no future layer mistakes them for computed truth.
7. **Document the canonical lifecycle state machine (A16).**

---

## 9. Bottom line

None of these assumptions are signs of a broken system — they are the expected
shape of an **Early Semantic Runtime**. The danger is not their existence; it is
**pretending they aren't there.** The progress numbers are coverage estimates, not
physics; readiness is a hint, not a guarantee; confidence is a label, not a measure;
blockers are notes, not gates; and there is no dependency network underneath any of
it. Documenting that plainly is what lets BetavanX evolve without building its next
intelligence layer on a foundation it only pretended to have.

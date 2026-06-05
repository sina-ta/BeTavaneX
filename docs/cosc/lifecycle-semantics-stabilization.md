# COSC — Lifecycle Semantics Stabilization

> The **authoritative operational meaning** of lifecycle behavior across BetavanX:
> what each entity's states *mean*, which transitions are real, who owns them, and —
> the central concern — what "started" and "completed" actually mean across truth
> layers.
>
> **Semantic definition only.** No state machine, no lifecycle engine, no propagation,
> no scheduler, no workflow redesign, no runtime changes. Where the authoritative
> meaning and the runtime diverge, the gap is marked (**Gap**) and left unimplemented.

## Relationship to the other COSC docs

- `lifecycle-semantics.md` answered **"what states/transitions exist today?"**
  (Enforced vs Set-only).
- This document answers **"what is each lifecycle *allowed to mean*, authoritatively?"**
  and resolves the **five-way conflation of "completion."**

Grounded in: `lifecycle-semantics.md`, `truth-reconciliation-semantics.md`,
`dependency-semantics-stabilization.md`, `operational-philosophy.md`,
`core-operational-decisions.md` (axioms), `event-taxonomy.md`,
`operational-assumption-registry.md`.

The governing axioms: **reality precedes governance** (axiom #3), **progress is
derived not declared** (axiom #4), **truth is layered** (philosophy #8), and **failure
≠ deletion** (truth-reconciliation §1) — lifecycles end in a *terminal status*, never
row removal.

---

## 1. Operational Lifecycle Model

A lifecycle is a layered story, not one status column. Authoritatively, every entity's
lifecycle is read across the truth layers from `truth-reconciliation-semantics.md`:

```
Structural lifecycle   exists → (terminal status)        [never deleted]
Execution lifecycle    not-started → in-progress → executed   (derived from reality)
Governance lifecycle   un-accepted → accepted / rejected / rework   (authority acts)
Reporting lifecycle    observed → submitted → reviewed/accepted     (observations)
Lineage lifecycle      append-only record of every transition       (immutable)
```

Authoritative principles:
1. **One status column ≠ the lifecycle.** A `WorkflowStep` has *four* concurrent
   lifecycles (structural existence, execution progress, governance status, readiness)
   that the runtime stores as separate fields and must be read together.
2. **Lifecycles are owned per the one-writer rule** (`truth-contracts.md`): each
   transition has exactly one authoritative writer.
3. **Lifecycles terminate in status, not deletion.** The only deletable carriers are
   the two junctions (`WorkOrderWorkflowStep`, `BOQMapping`).
4. **Governance lifecycle validates execution lifecycle; it never rewrites it**
   (axiom #3).

---

## 2. Entity Lifecycle Definitions

For each entity: the 13 stabilized properties. "**Gap**" = runtime does not honor the
authoritative meaning (set-only where authority is implied). States/transitions taken
verbatim from `lifecycle-semantics.md`.

### 2.1 Project
1. **Purpose.** The top-level operational container and intent frame.
2. **Authority.** Planning (`PlanningUseCases`); admin/supervisor.
3. **States.** `DRAFT, ACTIVE, ON_HOLD, COMPLETED, CANCELLED` (default `ACTIVE`).
4. **Transition meaning.** Movement of *intent*, not execution reality (philosophy #1).
5. **Allowed.** `DRAFT→ACTIVE→ON_HOLD↔ACTIVE→COMPLETED/CANCELLED`.
6. **Forbidden (authoritative).** Re-activating a `CANCELLED` project; marking
   `COMPLETED` while child execution is incomplete. **Gap:** set-only, nothing guards.
7. **Reversible / irreversible.** `ON_HOLD` reversible; `COMPLETED`/`CANCELLED` are
   authoritatively terminal (convention-terminal today).
8. **Governance interaction.** None direct; project completion is a *derived* judgment
   over children, not a governance act.
9. **Dependency interaction.** Containment root; cannot be deleted with children.
10. **Progress interaction.** Project progress is the unweighted mean of activity
    progress (derived) — independent of the `COMPLETED` header flag.
11. **Contradiction semantics.** `Project.COMPLETED` with child progress < 100 is a
    **derived-vs-header contradiction** (allowed but must be surfaced).
12. **Lineage expectations.** Creation is a `planning` audit record; status changes
    should be lineage events (only create is recorded today).
13. **Historical preservation.** Never deleted; terminal status preserved forever.

### 2.2 ActivityInstance
1. **Purpose.** The unit of located work (WBS×Location); the roll-up point for steps.
2. **Authority.** Planning.
3. **States.** `ACTIVE, COMPLETED, CANCELLED` (default `ACTIVE`).
4. **Transition meaning.** A *header* declaration; real advancement lives in child
   steps.
5. **Allowed.** `ACTIVE→COMPLETED/CANCELLED`.
6. **Forbidden (authoritative).** `COMPLETED` while child steps are not operationally
   complete. **Gap:** set-only.
7. **Reversible / irreversible.** `COMPLETED`/`CANCELLED` authoritatively terminal.
8. **Governance interaction.** None; completion is derived, not governed.
9. **Dependency interaction.** Spatial (WBS×Location uniqueness); contains steps.
10. **Progress interaction.** Progress is **derived** from child steps and **not
    stored** here — completion flag and derived progress are two truths (A17).
11. **Contradiction semantics.** `ACTIVE` header at 100% derived progress, or
    `COMPLETED` header at <100% — both allowed, both must be surfaced.
12. **Lineage expectations.** Status changes should be lineage events (not recorded
    today).
13. **Historical preservation.** Never deleted.

### 2.3 WorkflowStep — the governed, multi-lifecycle entity
1. **Purpose.** The atom of execution and governance; the coordination structure
   (philosophy #5).
2. **Authority.** **Split:** planning creates; `WorkflowGovernanceService` owns
   governance transitions; `ProgressService` owns progress; **readiness is unowned**
   (Gap, A4).
3. **States.** `PLANNED, IN_PROGRESS, COMPLETED, INSPECTION_PENDING,
   INSPECTION_FAILED, REWORK_REQUIRED, APPROVED` + `ready: bool` + `progress_percent`.
4. **Transition meaning.** Three *separate* lifecycles in one row: execution
   (`PLANNED→IN_PROGRESS→COMPLETED`), governance
   (`INSPECTION_PENDING→APPROVED` / `INSPECTION_FAILED→REWORK_REQUIRED`), and progress
   (0→100, derived).
5. **Allowed (authoritative).** Execution: PLANNED→IN_PROGRESS→COMPLETED. Governance:
   COMPLETED→INSPECTION_PENDING→(passed→APPROVED | failed→INSPECTION_FAILED→REWORK_REQUIRED→IN_PROGRESS).
6. **Forbidden (authoritative).** `APPROVED` from arbitrary states; `APPROVED` without
   inspection precedence; `APPROVED` over an open disqualifying blocker; being "born"
   `COMPLETED`/`APPROVED` at creation. **Gap:** all currently possible (only
   `INSPECTION_PENDING→APPROVED` and duplicate-approval are guarded; invalid patterns
   #4/#5).
7. **Reversible / irreversible.** `REWORK_REQUIRED` and `INSPECTION_FAILED` are
   legitimate **governance regressions**. `APPROVED` is authoritatively terminal for
   acceptance — but rework after approval should be a *new* governance act, not a
   silent backward set (Gap).
8. **Governance interaction.** The governed lifecycle; approval/inspection/rework are
   authority acts.
9. **Dependency interaction.** Execution dependency (work-order weight → progress);
   governance dependency; readiness dependency (should gate, doesn't).
10. **Progress interaction.** `progress_percent` is a **cache** over recomputation;
    independent of `status`. A step can be `APPROVED` at 0% or `PLANNED` at 100%.
11. **Contradiction semantics.** The richest contradiction surface: status vs progress
    vs cache vs readiness. All allowed-but-surfaced except the safety case (`APPROVED`
    + open `CRITICAL` blocker), which is authoritatively forbidden (A5).
12. **Lineage expectations.** `approval_completed` recorded; inspection pass/fail,
    rework, and execution start/finish should be lineage events with
    `causality_reference` threading rework→failed-inspection.
13. **Historical preservation.** Never deleted; every governance transition auditable
    forever.

### 2.4 WorkOrder — the execution-completion hinge
1. **Purpose.** The field commitment that carries `execution_weight`; the source of
   execution-completion truth.
2. **Authority.** Planning creates; callers/execution drive status;
   `WorkflowExecutionService` owns the link.
3. **States.** `CREATED, ASSIGNED, IN_PROGRESS, COMPLETED, CANCELLED` (default
   `CREATED`).
4. **Transition meaning.** The *execution* lifecycle of a commitment.
   `COMPLETED` is the single hinge of all progress arithmetic.
5. **Allowed.** `CREATED→ASSIGNED→IN_PROGRESS→COMPLETED/CANCELLED`.
6. **Forbidden (authoritative).** Silent regression out of `COMPLETED` without a
   reconciliation event (it changes every dependent progress denominator — invalid
   pattern #7). **Gap:** set-only, no reconciliation event.
7. **Reversible / irreversible.** `COMPLETED` should be effectively irreversible
   *without an explicit, lineage-recorded reversal*; `CANCELLED` terminal.
8. **Governance interaction.** None direct; `COMPLETED` is **execution** truth, not
   governance — it does not require approval to be true (axiom #3).
9. **Dependency interaction.** Its weight enters a step's progress only via a
   coordination link; cross-project links are authoritatively forbidden (invalid
   pattern #1).
10. **Progress interaction.** **Binary contribution:** weight counts only at
    `COMPLETED` — no partial (A2). This is the coarsest lifecycle assumption.
11. **Contradiction semantics.** `WorkOrder.COMPLETED` vs a step still `IN_PROGRESS`
    vs `progress<100` — the core of the three-"done" conflation (A17).
12. **Lineage expectations.** Assignment recorded (`work_order_assigned`); completion
    should be a lineage event (the raw material for future timing/rate — currently
    absent, A8).
13. **Historical preservation.** Never deleted.

### 2.5 DailyReport — reporting lifecycle (observation)
1. **Purpose.** Field evidence; an *observation*, not a verdict (philosophy #2).
2. **Authority.** `WorkflowExecutionService`; worker/supervisor/admin.
3. **States.** `DRAFT, SUBMITTED, REVIEWED, ACCEPTED, REJECTED` (default `DRAFT`).
4. **Transition meaning.** The maturation of an observation toward acceptance — not of
   execution itself.
5. **Allowed.** `DRAFT→SUBMITTED→REVIEWED→ACCEPTED/REJECTED`.
6. **Forbidden (authoritative).** Treating `ACCEPTED` as execution completion. A report
   is evidence feeding execution truth, never execution truth itself.
7. **Reversible / irreversible.** `REJECTED` may be superseded by a new report; reports
   themselves are append records.
8. **Governance interaction.** Review/acceptance is a light governance act over the
   *observation*, distinct from step approval.
9. **Dependency interaction.** Informational dependency (feeds analytics);
   created under the parent **work order's** optimistic token.
10. **Progress interaction.** **None directly** — reporting does not move progress;
    only work-order `COMPLETED` does (a notable gap between observation and execution
    truth).
11. **Contradiction semantics.** A report asserting work not reflected in progress is
    an allowed reporting-vs-execution contradiction (truth-reconciliation §2.3).
12. **Lineage expectations.** `daily_report_submitted` recorded; review/accept should
    be lineage events.
13. **Historical preservation.** Append-only evidence; never deleted, even if
    superseded.

### 2.6 Approval — governance-completion record
1. **Purpose.** The record of an acceptance authority act.
2. **Authority.** `WorkflowGovernanceService`; admin/supervisor.
3. **States.** `PENDING, UNDER_REVIEW, APPROVED, REJECTED`.
4. **Transition meaning.** Governance acceptance of execution — *validation, not
   reality creation* (axiom #3).
5. **Allowed (authoritative).** `PENDING→UNDER_REVIEW→APPROVED/REJECTED`.
6. **Forbidden (authoritative).** Duplicate `APPROVED` of same type (guarded);
   approval whose attribution is unverifiable. **Gap:** live path creates `APPROVED`
   directly (skipping `PENDING/UNDER_REVIEW`), and `approved_by` is client-supplied
   (A18).
7. **Reversible / irreversible.** `APPROVED`/`REJECTED` terminal for that approval
   record; a reversal is a *new* governance act, never an edit.
8. **Governance interaction.** It *is* governance completion.
9. **Dependency interaction.** Governance dependency on the step; should consult
   readiness/blockers (Gap, A15).
10. **Progress interaction.** None — approval and progress are independent truths.
11. **Contradiction semantics.** `APPROVED` at low progress is allowed-but-flagged;
    `APPROVED` over open `CRITICAL` blocker is forbidden (A5).
12. **Lineage expectations.** `approval_completed` recorded with server-derived actor
    (attribution gap today).
13. **Historical preservation.** Never deleted; the canonical "who accepted what, when"
    forever.

### 2.7 Blocker — execution-friction lifecycle
1. **Purpose.** Operationally meaningful execution friction (philosophy #7), not a
   generic ticket.
2. **Authority.** `WorkflowGovernanceService`.
3. **States.** `OPEN, ACKNOWLEDGED, MITIGATION_IN_PROGRESS, RESOLVED, CLOSED, REOPENED`
   + severity `LOW..CRITICAL`.
4. **Transition meaning.** The life of an impediment from detection to resolution.
5. **Allowed.** `OPEN→ACKNOWLEDGED→MITIGATION_IN_PROGRESS→RESOLVED→CLOSED`;
   `RESOLVED/CLOSED→REOPENED` (legitimate regression).
6. **Forbidden (authoritative).** None structurally; but an open disqualifying blocker
   **should** constrain readiness and block governance acceptance (Gap, A5).
7. **Reversible / irreversible.** `REOPENED` is an explicit, valid reversal; `CLOSED`
   is soft-terminal.
8. **Governance interaction.** `resolve_blocker` is the only enforced transition;
   authoritatively an open `CRITICAL` blocker is a governance gate (not enforced).
9. **Dependency interaction.** Authoritatively a **soft readiness constraint**
   (dependency-stabilization §5); today inert (A5) — affects only analytics.
10. **Progress interaction.** **None** — blockers do not move or freeze progress.
11. **Contradiction semantics.** Open blocker + `ready=true` / + `APPROVED` are the key
    escalation contradictions.
12. **Lineage expectations.** `blocker_registered` / `blocker_resolved` recorded;
    resolution should `causality_reference` the registration.
13. **Historical preservation.** Never deleted; friction history preserved forever.

### 2.8 Assignment (`WorkOrderWorkflowStep`) — junction lifecycle
1. **Purpose.** Binds a work order's weight to a step; the unit of field coordination.
2. **Authority.** `WorkflowExecutionService`.
3. **States.** No status — lifecycle is **exists / removed** (one of two deletable
   carriers).
4. **Transition meaning.** Creation admits weight into the step's progress; removal
   withdraws it.
5. **Allowed.** create (unique pair) → remove.
6. **Forbidden (authoritative).** Duplicate `(work_order, step)` (guarded + alerted);
   **cross-project link** (authoritatively forbidden — invalid pattern #1, **Gap**).
7. **Reversible / irreversible.** Fully reversible (removable) — by design, this is the
   correction mechanism.
8. **Governance interaction.** None; pure coordination structure.
9. **Dependency interaction.** Coordination link (Hard) feeding execution dependency.
10. **Progress interaction.** Creating/removing a link **changes the denominator** of
    the step's progress formula.
11. **Contradiction semantics.** A removed link silently changes historical progress
    arithmetic — reconciliation should be lineage-recorded.
12. **Lineage expectations.** Assignment recorded; removal should also be a lineage
    event.
13. **Historical preservation.** The *event* of assignment/removal is preserved in
    lineage even though the junction row itself is deletable — lineage outlives the row.

---

## 3. Lifecycle Authority Matrix

| Entity | Lifecycle owner (writer) | Transition class | Enforced today? |
|---|---|---|---|
| Project | `PlanningUseCases` | Planning intent | Set-only |
| ActivityInstance | `PlanningUseCases` | Planning + derived completion | Set-only |
| WorkflowStep (execution) | callers / planning | Execution | Set-only |
| WorkflowStep (governance) | `WorkflowGovernanceService` | Governance | Partly enforced |
| WorkflowStep (progress) | `ProgressService` | Derived | Computed |
| WorkflowStep (readiness) | **none** | Derived (should be) | **Unowned (Gap)** |
| WorkOrder | planning / callers | Execution | Set-only |
| DailyReport | `WorkflowExecutionService` | Reporting/observation | Set-only |
| Approval | `WorkflowGovernanceService` | Governance | Partly enforced |
| Blocker | `WorkflowGovernanceService` | Friction | One enforced transition |
| Assignment | `WorkflowExecutionService` | Coordination (exists/removed) | Enforced (dup-guard) |

Authoritative reading: **only governance, progress, and the junction guards are real
enforcement**; everything else is convention (set-only). The single most important
ownership gap is **readiness has no owner**.

---

## 4. Transition Semantics

1. **Transitions are authority acts.** A transition is owned by exactly one writer; no
   other layer may perform it (one-writer rule).
2. **Execution transitions describe reality** and need no governance permission
   (axiom #3): a work order can become `COMPLETED` without any approval.
3. **Governance transitions validate reality** and are the only ones that may *gate*
   (acceptance), never gate the physical act.
4. **Derived transitions are computed, not set.** Progress moves by recomputation
   (`ProgressService`); it is never a declared transition.
5. **Set-only ≠ authoritative.** A value being in the CHECK list does not make the
   transition legitimate; the authoritative ordering above is the contract the runtime
   does not yet enforce.
6. **Regression is legitimate only when explicit and owned** (rework, reopen, failed
   inspection). Silent backward set-only moves are fragility, not lifecycle.

---

## 5. Completion Semantics (special focus)

The runtime conflates **five distinct completions**. Authoritatively they are
separate truths and must never be assumed equal (A17, truth-reconciliation §4).

| Completion type | Authoritative signal | Owner / layer | Means |
|---|---|---|---|
| **Execution completion** | `WorkOrder.status = COMPLETED` (→ step `progress = 100`) | Execution truth (`ProgressService`) | the work was *physically done* |
| **Governance completion** | `WorkflowStep.status = APPROVED` / `Approval.APPROVED` | Governance truth (`WorkflowGovernanceService`) | the work was *accepted/authorized* |
| **Reporting completion** | `DailyReport.status = ACCEPTED` | Reporting truth | an *observation* of work was accepted |
| **Derived completion** | `progress_percent = 100`; `ActivityInstance/Project = COMPLETED` | Derived/header | an *interpretation/roll-up* says done |
| **Historical completion** | terminal status preserved in lineage forever | Lineage truth | it is *recorded* as having completed |

Authoritative rules:
- **Execution completion can precede governance completion** (axiom #3). Done ≠
  approved.
- **No completion implies another.** `WorkOrder.COMPLETED` does not make the step
  `APPROVED`; `APPROVED` does not make `progress = 100`; `progress = 100` does not mark
  the activity `COMPLETED`.
- **Derived completion (`progress=100`) is the weakest** — it is a cache over
  recomputation and must yield to the recomputation (A3).
- **Header completion (`ActivityInstance/Project.COMPLETED`) is a planning
  declaration**, authoritatively reconcilable against derived child progress, not a
  substitute for it.
- **"Operationally complete"** = execution completion corroborated by evidence;
  **"formally complete"** = governance completion. A platform statement of "done" must
  say *which*.

### What counts as "started"?
Authoritatively, **started = first real execution evidence exists** — a work order
moved to `IN_PROGRESS` *or* a daily report was submitted against it — **not** a status
flip alone. **Gap:** there is no automatic `PLANNED → IN_PROGRESS` driver; "started" is
currently whatever a caller set (convention). Header status `IN_PROGRESS` without any
report/assignment is *declared*, not *started*.

---

## 6. Lifecycle Contradiction Rules

Applying truth-reconciliation to lifecycles:

- **Allowed (surface, never auto-resolve):**
  - execution complete, governance not (done, not `APPROVED`),
  - governance complete, execution not (`APPROVED`, `progress<100`),
  - header `COMPLETED` vs derived child progress <100,
  - reporting `ACCEPTED` vs progress unchanged.
- **Forbidden (structural / safety invariants):**
  - `APPROVED` over an open `CRITICAL`/disqualifying blocker (safety — A5),
  - a step "born" `APPROVED`/`COMPLETED` with no underlying execution (invalid pattern
    #5),
  - cross-project commitment counting (invalid pattern #1),
  - silent regression out of a terminal/`COMPLETED` state with no lineage event.
- **Regression policy:** lifecycle states **may regress** only through an explicit,
  owned, lineage-recorded act (`REWORK_REQUIRED`, `REOPENED`, `INSPECTION_FAILED`).
  Silent backward set-only is not a legitimate regression.

---

## 7. Governance & Dependency Interactions

- **Governance-required transitions:** approval, inspection pass/fail, rework, blocker
  resolution. These are the only transitions that carry acceptance authority.
- **Non-governance transitions:** all execution (work order, step execution states),
  reporting, assignment — these describe reality/observation and require no approval to
  be true (axiom #3).
- **Dependency interactions:** completion propagates **only** bottom-up via execution
  dependency (step→activity→project, unweighted — A1) and governance propagates **only**
  to the step (no hierarchy cascade). Readiness/resource/blocker *should* constrain
  governance acceptance (soft); today they do not (Gaps A4/A5/A15).
- **Observational-only states:** `DailyReport` and `Inspection` states are observations;
  analytics-inferred states (`Approval.PENDING/UNDER_REVIEW` in detection) are *not even
  produced* by the write path (invalid pattern #8) — observational dependency on an
  unreachable state.

---

## 8. Event Lineage Expectations

**No implementation here** — expectations for when transitions are recorded:

1. **Every authority transition should emit a lineage event** (the ledger already has
   `work_order_assigned`, `daily_report_submitted`, `approval_completed`,
   `blocker_registered/resolved`). Missing but expected: execution start/finish,
   inspection pass/fail, rework, status changes on Project/Activity, assignment removal.
2. **Regressions thread causality.** A rework event should `causality_reference` the
   failed inspection; a `REOPENED` blocker should reference its prior resolution.
3. **Completion is a lineage milestone**, not just a column flip — execution completion
   and governance completion should each be recorded so the *five completions* are
   independently traceable.
4. **Append-only.** A lifecycle never rewrites history; every transition (including
   regressions) is a new immutable record (`event-ledger-foundation.md`).

---

## 9. Historical Preservation Semantics

1. **Failure ≠ deletion.** Rework, rejection, failed inspection, reopened blockers are
   *states*, never row removals. Lifecycle ends in terminal status.
2. **Only junctions are deletable** (`WorkOrderWorkflowStep`, `BOQMapping`) — but their
   *assignment/removal events* are preserved in lineage; lineage outlives the row.
3. **Terminal states are preserved forever** and remain queryable; a `COMPLETED`/
   `CANCELLED`/`CLOSED` record is history, not garbage.
4. **Attribution is part of history.** Who drove each transition must be retained even
   if the user record changes (soft attribution today — should be server-derived, A18).
5. **What must remain auditable forever:** all governance acts (approval, inspection,
   rework, blocker resolution), all completions (execution + governance), and all
   regressions. These are the operational record of the project.

---

## 10. Resolved Questions

1. **What operationally counts as "started"?** First real execution evidence (work
   order `IN_PROGRESS` *or* a submitted daily report) — not a status flip alone. Today
   "started" is convention (no auto-driver).
2. **What operationally counts as "completed"?** Depends which completion (§5):
   *execution* (work physically done, `WorkOrder.COMPLETED`→`progress=100`), *governance*
   (`APPROVED`), *reporting* (`ACCEPTED`), *derived* (header/cache), *historical*
   (lineage). A statement of "done" must name the layer.
3. **Can execution complete before governance completion?** **Yes** (axiom #3) — done
   before approved is valid and expected.
4. **Can lifecycle states conflict across truth layers?** **Yes** — status vs progress
   vs governance vs reporting may disagree; allowed-but-surfaced except safety cases.
5. **Can lifecycle states regress?** **Yes**, but only via explicit owned,
   lineage-recorded acts (rework, reopen, failed inspection). Silent backward set-only
   is illegitimate.
6. **Which transitions require governance?** Approval, inspection pass/fail, rework,
   blocker resolution. Execution/reporting/assignment do not.
7. **Which lifecycle states are observational only?** `DailyReport` and `Inspection`
   states; analytics-inferred `Approval.PENDING/UNDER_REVIEW` (not produced by writes).
8. **Which transitions must remain auditable forever?** All governance acts, all
   completions (execution + governance), and all regressions — append-only.

---

## 11. Future Runtime Stabilization Implications

Deltas between this contract and the runtime — **boundaries, not built here**, each
strengthening an existing owner:

1. **Separate the five completions explicitly** in the read model / contracts so "done"
   always names its layer (A17). No new state.
2. **Define a canonical state machine for `WorkflowStep`** (execution + governance) so
   set-only backward moves and "born approved" become illegitimate (invalid patterns
   #4/#5). Owner: `WorkflowGovernanceService`.
3. **Govern `WorkOrder.COMPLETED` reversal** with a reconciliation event (it changes
   every dependent denominator — invalid pattern #7).
4. **Give readiness an owner** so it is a derived lifecycle, not an unowned flag (A4).
5. **Make completion auditable as lineage milestones** (execution + governance), not
   just column flips.
6. **Define ActivityInstance/Project completion as derived-reconcilable**, not a free
   header flip, against child progress.
7. **Server-derive transition attribution** (A18) so historical preservation is
   trustworthy.

Each lives within current service ownership — none requires a lifecycle engine, state
machine framework, or orchestration runtime. Stabilizing the *meaning* first tells
future enforcement exactly which transitions are authority acts, which are derived, and
which must be recorded forever.

---

## 12. Bottom line

BetavanX has exactly one genuinely governed lifecycle (`WorkflowStep`) and a field of
**set-only status columns the database constrains by value but not by order.** The
deeper issue is not weak enforcement — it is that **"completion" means five different
things** (execution, governance, reporting, derived, historical) that the runtime
quietly treats as interchangeable. Authoritatively: lifecycles are layered, each
transition has one owner, execution completion can precede governance completion,
regression is legitimate only when explicit and recorded, and every authority act and
completion is preserved in immutable lineage forever. Nothing here changes the runtime
— it fixes what the states *mean* so that when enforcement is added it strengthens the
existing owners and never lets a header flip, a stale cache, or a convention masquerade
as operational truth.

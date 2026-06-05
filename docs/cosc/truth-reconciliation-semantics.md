# COSC — Truth Reconciliation Semantics

> How conflicting operational truths **coexist, interact, escalate, and reconcile**
> in BetavanX. This defines *behavior under conflict* — not software that resolves
> conflict automatically.
>
> **Semantic definition only.** No conflict engine, no AI arbitration, no consensus
> system, no distributed events, no automatic resolution, no runtime changes. Where
> the authoritative semantics and the current runtime diverge, the gap is marked
> (**Gap**) and left unimplemented.

## Grounding

Built on and consistent with: `operational-philosophy.md`,
`core-operational-decisions.md` (axioms), `truth-contracts.md`,
`dependency-semantics-stabilization.md`, `operational-assumption-registry.md`,
`event-taxonomy.md`, `lifecycle-semantics.md`.

The two axioms this entire document rests on:

- **Reality precedes governance** (philosophy #1, axiom #3): operational reality can
  exist before — and temporarily in conflict with — its governance acknowledgement.
- **Truth is layered and shared** (philosophy #8): multiple operational perspectives
  coexist, may conflict, and are *reconciled progressively*. No single actor owns all
  truth.

Therefore contradiction is **not a bug to be eliminated**. It is a normal state to be
**surfaced, attributed, and reconciled** — never silently collapsed.

---

## 1. Operational Truth Layer Model

Seven layers. Each is defined by **authority** (how binding), **ownership** (the only
writer, from `truth-contracts.md`), **mutability**, and **reconciliation role**.

| Layer | What it asserts | Authority | Owner (only writer) | Mutability | Reconciliation role |
|---|---|---|---|---|---|
| **Structural truth** | "this exists / is unique / belongs here" | **Invariant** | PostgreSQL constraints + `delete_policy` | Immutable invariant | Cannot be reconciled — only *prevented*. No conflict tolerated. |
| **Planning truth** | intended scope/structure (projects, WBS, location, BOQ, activity plan) | Intent | `PlanningUseCases` | Mutable by planning | Defines the frame; yields to execution reality (philosophy #1). |
| **Execution truth** | what physically advanced (progress, commitments) | **Operational truth** | `ProgressService` (progress), `WorkflowExecutionService` (commitments/links) | Derived (progress) / appended (commitments) | The reality layer. Reconciled by **recomputation**, not by decree. |
| **Reporting truth** | field observations (daily reports) | Observation | `WorkflowExecutionService` | Append (immutable record) | Evidence feeding execution truth; **not automatically truth** (philosophy #2). |
| **Governance truth** | accepted/authorized state (approval, inspection, status) | **Authoritative acceptance** | `WorkflowGovernanceService` (+ planning create) | Mutable by governance acts | Validates/authorizes execution truth; **may not rewrite it** (axiom #3). |
| **Lineage truth** | that an action happened, by whom, when (audit, usage, event ledger) | Record | audit/usage stores; `EventRecordingService` (ledger) | **Append-only, immutable** | The evidentiary spine reconciliation is judged against. |
| **Analytical interpretation** | inferred signals/health/coordination | **Advisory** | analytics services (read-only) | Recomputed, never stored as truth | Detects and *surfaces* contradiction; **never reconciles or mutates**. |

Two structural facts from `truth-contracts.md` govern all of the above:
1. **One writer per authoritative field.** A layer "owns" a fact; other layers may
   disagree *about overlapping reality* but cannot write that field.
2. **Derived values are never independent truth** — progress is a cache over a
   recomputation; analytics carry `false_positive_notes`.

---

## 2. Contradiction Taxonomy

### 2.1 What counts as a contradiction
A contradiction is **two layers making incompatible claims about the same operational
reality** — not two unrelated facts. Examples that are real in this runtime:

- `progress = 100` (execution) vs `status ≠ APPROVED` (governance) — and the inverse.
- `WorkOrder.COMPLETED` vs `WorkflowStep` progress that doesn't reflect it (the
  three definitions of "done", A17).
- `ready = true` (readiness) vs an open `CRITICAL` blocker (friction).
- A `DailyReport` asserting work (reporting) not reflected in progress (execution).
- An analytics signal inferring `PENDING` approvals that the write path never creates
  (interpretation vs reality — `event-taxonomy.md` 4b, invalid pattern #8).
- A cached `progress_percent` disagreeing with a fresh recomputation (stale derived
  truth, A3).

### 2.2 Temporary vs critical contradiction
- **Temporary (benign):** a normal lag between layers that will reconcile through the
  ordinary flow — e.g. progress lagging a just-completed work order until recompute;
  status not yet `APPROVED` for finished work awaiting inspection.
- **Critical (operational risk):** a contradiction that, if trusted, causes harm or
  cannot self-reconcile — e.g. `APPROVED` over an open `CRITICAL` blocker (A5);
  payment/reporting on stale progress; "ready" work that is actually blocked.

### 2.3 Allowed contradiction states
Permitted to exist (must be surfaced, never auto-resolved):
- execution vs governance (reality ahead of, or behind, acceptance),
- reporting vs execution (an observation pending incorporation),
- analytics vs any layer (interpretation flags a discrepancy).

### 2.4 Invalid contradiction states
Must never occur (structural invariants):
- a child without its parent (containment),
- two activities at one WBS×Location (spatial uniqueness),
- a commitment's weight counting across **different projects** (invalid pattern #1 —
  currently *possible*, authoritatively *forbidden*),
- duplicate `APPROVED` of the same `approval_type` (already blocked).

### 2.5 Unresolved contradiction behavior
An unresolved contradiction **may persist** (philosophy #8) under one condition: it is
**visible and attributed**. The forbidden states are *silent* unresolved contradiction
and *automatic* resolution. Persistence is acceptable; concealment is not.

---

## 3. Reconciliation Authority Matrix

Who may reconcile which conflict, and by what act. (Roles per
`operational-philosophy.md` authority section.)

| Conflict | Reconciled by | Mechanism (existing) | May NOT |
|---|---|---|---|
| Structural violation | **Nobody** — prevented | DB constraints reject the write | be "reconciled" after the fact |
| Execution vs cache (stale progress) | **System** (derived) | `ProgressService` recomputation | be set by a human decree |
| Reporting vs execution | **System + Supervisor** | recompute on completion; supervisor validates the report | analytics auto-deciding |
| Execution vs governance | **Governance** (supervisor/admin) | `approve` / inspection / `REWORK_REQUIRED` | rewrite progress to match status |
| Readiness vs blocker | **Supervisor** (governance) | resolve/мitigate blocker, re-derive readiness | flip `ready` without basis (Gap, A4) |
| Concurrency conflict | **System** | optimistic `updated_at` token → `409` | last-write-wins silently (opt-in gap) |
| Analytics vs reality | **No reconciliation** | analytics are advisory; flagged, not resolved | mutate any domain state |

Authoritative principles:
- **Governance reconciles acceptance, not reality.** Approval/rejection changes
  *governance truth*; it never edits execution truth or lineage (axiom #3).
- **Execution reconciles by recomputation.** Progress is realigned by recomputing from
  commitments — not by anyone declaring a number (axiom #4).
- **Evidence is the basis, lineage is the record.** Daily reports + the event ledger
  are what a reconciler judges against; both are append-only.
- **Analytics never reconcile.** They detect and surface; they are read-only leaves
  (`truth-contracts.md`).
- **Every reconciliation is an authority act** → it must be attributed and auditable
  (§9).

---

## 4. Truth Precedence Rules

Precedence answers: *when two layers describe the same reality, which one is believed,
and which may change which.*

```
Structural truth      ── absolute; overrides nothing because it is never in conflict
        ▲
Execution truth       ── reality; governance VALIDATES it but cannot OVERWRITE it
        ▲
Reporting truth       ── evidence INTO execution; not authoritative on its own
        ▲
Governance truth      ── authoritative on ACCEPTANCE; validates, never fabricates reality
        ▲
Lineage truth         ── records all of the above; immutable; arbitration evidence
        ▲
Analytical interp.    ── advisory; may contradict any layer; can mutate NONE
```

Rules:
1. **Structural truth is absolute.** It cannot be contradicted, only prevented.
2. **Execution truth represents reality** (philosophy #1). Governance may *withhold
   acceptance* of it but **cannot overwrite it** — a step can be 100% executed and
   un-approved, or approved and 0% executed; both stand, surfaced as contradiction.
3. **Governance is authoritative over acceptance only.** `APPROVED` is the truth of
   "authorized," never the truth of "physically done."
4. **Reporting validates upward, never decrees.** A report is an observation whose
   reliability depends on actor authority, evidence, and corroboration (philosophy
   #2); it feeds execution truth, it is not execution truth by itself.
5. **Analytics can override nothing.** Lowest precedence; advisory always
   (`event-taxonomy.md` boundary rules).
6. **Derived ≠ primary.** A cached derived value (progress cache) yields to its
   recomputation; the cache never wins (A3).
7. **No layer may silently mutate another layer's field** (one-writer rule).

---

## 5. Confidence & Evidence Semantics

Defined **without any scoring system** — qualitative semantics only.

### 5.1 Confidence-aware observations
A report/observation is not binary truth (philosophy #2). Its **confidence** is a
qualitative function of:
- **actor authority** (worker observes; supervisor governs — philosophy authority
  model),
- **supporting evidence** (daily report, attachments, event lineage),
- **corroboration** (multiple independent observations agree),
- **contradiction presence** (a conflicting signal lowers confidence),
- **governance validation** (an approved observation carries acceptance weight).

### 5.2 Evidence weighting (qualitative ordering)
Authoritative ordering of believability, **not** a numeric scale:

```
corroborated evidence + governance validation
  > corroborated evidence
    > single authoritative observation (e.g. supervisor report)
      > single field observation (worker report)
        > bare declaration with no evidence
          > analytic inference
```

### 5.3 Uncertainty awareness
Uncertainty is **named, not measured**:
- derived values carry **staleness uncertainty** (progress cache may be old — A3),
- analytics carry **interpretation uncertainty** (`false_positive_notes`,
  `data_available: false` when the DB is absent),
- declarations carry **attribution uncertainty** (`approved_by`/`reported_by` are soft
  UUIDs — "who *claimed* to act", `truth-contracts.md` identity truth, A18).

### 5.4 Contradictory evidence handling
When evidence conflicts: **surface both, collapse neither.** The effective confidence
of the claim drops; the contradiction is recorded; a human/governance act (not the
system) decides. The platform must never silently pick a winner. (This is the semantic
of "confidence-weighted operational truth" in philosophy #2 — defined here, not
implemented.)

---

## 6. Escalation Rules

When a contradiction stops being benign.

| Condition | Becomes | Authoritative consequence | Runtime today |
|---|---|---|---|
| Layers lag but will self-reconcile | Acceptable | Surface; no action | OK (no surfacing UI, but harmless) |
| Disqualifying blocker open at acceptance | **Operational risk** | **Should block governance** acceptance | **Gap** — not blocked (A5/A15) |
| Failed inspection vs prior approval | Operational risk | Route to `REWORK_REQUIRED`; record reconciliation | Partial (rework exists; precedence not enforced) |
| Stale progress drives decision/payment | **Operational risk** | Recompute before trusting; flag staleness | **Gap** — cache trusted (A3) |
| Analytics infer non-existent state | Noise risk | Mark advisory; correct the inference | Partial (`false_positive_notes`) |
| Concurrency collision | Risk | Block write, `409`, audit `conflict` | OK (opt-in) |

Authoritative escalation principles:
- **Contradiction blocks execution: never.** Reality happens regardless of disputes;
  the physical act of execution is never gated by a truth conflict (axiom #3).
- **Contradiction blocks governance: when a disqualifying condition is unresolved.**
  An open `CRITICAL` blocker, a failed inspection, or unmet precedence *should* block
  `APPROVED` (authoritative; **Gap** today — governance is bypassable).
- **Contradiction is acceptable** when it is transient and self-reconciling, provided
  it is visible.

---

## 7. Allowed vs Forbidden Contradictions

| Contradiction | Verdict | Why |
|---|---|---|
| Execution ahead of governance (`done`, not `APPROVED`) | **Allowed** | Reality precedes acknowledgement (axiom #3) |
| Governance ahead of execution (`APPROVED`, low progress) | **Allowed but flagged** | Acceptance ≠ reality; must be surfaced |
| Reporting ahead of execution recompute | **Allowed (transient)** | Evidence pending incorporation |
| Analytics vs any domain layer | **Allowed (advisory)** | Interpretation, lowest precedence |
| `ready=true` + open disqualifying blocker | **Allowed but is a risk** | Must escalate; should force "not ready" |
| Cached progress vs recomputation | **Allowed but cache loses** | Derived ≠ primary |
| `APPROVED` over open `CRITICAL` blocker | **Forbidden (authoritative)** | Safety; governance must consult friction — **Gap** |
| Child without parent | **Forbidden** | Structural invariant |
| Two activities at one WBS×Location | **Forbidden** | Spatial uniqueness |
| Commitment weight across projects | **Forbidden** | Aggregate integrity (invalid pattern #1) |
| Any layer silently overwriting another's field | **Forbidden** | One-writer rule |

---

## 8. Event Lineage Expectations

How contradictions and reconciliations *should* appear in lineage (the event ledger +
audit). **No implementation here** — these are expectations for when events are
recorded.

1. **Contradiction detection is already partly recorded.** Concurrency conflicts are
   audit records with `mutation_category = "conflict"` (`event-taxonomy.md` §1).
   That is the existing template for "a conflict happened."
2. **Reconciliation acts should be first-class lineage.** Approval, inspection
   pass/fail, rework, and blocker resolution are reconciliations of an
   execution/governance contradiction — they should each emit a ledger event
   (`approval_completed`, `blocker_resolved` already exist in the foundation).
3. **Causality threading.** A reconciling event should carry `causality_reference`
   (`event-ledger-foundation.md`) pointing to the event/state it reconciles — e.g. a
   `blocker_resolved` referencing the `blocker_registered` it closes; a rework
   referencing the failed inspection. This builds a *reconciliation lineage* without
   any conflict engine.
4. **Append-only, never edited.** A contradiction is never "deleted" from history; its
   resolution is a *new* event. Lineage shows the disagreement *and* its reconciliation
   side by side (consistent with the ledger's immutability guarantee).
5. **Surfacing, not resolving.** Analytics may emit a derived signal that a
   contradiction exists (e.g. `unresolved_blocker_communication`); this is observation,
   not a lineage truth-event, and must stay advisory.

---

## 9. Governance & Audit Expectations

1. **Every reconciliation is an authority act and must be attributed.** Who reconciled,
   when, on what basis — non-negotiable. (Today attribution is client-supplied and
   soft — A18, `truth-contracts.md` identity truth; authoritatively it should be
   server-derived.)
2. **Reconciliations are auditable and append-only.** They join the audit ledger
   (`governance` category) and the event ledger; neither is mutable.
3. **Governance reconciliation is bounded.** A supervisor/admin may change *acceptance*
   (approve, return to rework, resolve a blocker) — never the *execution record* or the
   *lineage*. Governance corrects the verdict, not the history.
4. **Analytics produce no audit truth.** Signals are recomputed and carry
   `false_positive_notes`; they are never recorded as reconciliations.
5. **Unresolved contradictions must remain queryable.** Acceptable persistence requires
   visibility — an unresolved contradiction that no one can see violates philosophy #8.

---

## 10. Resolved Questions

1. **Can execution reality exist before governance acknowledgement?** **Yes.** Reality
   precedes approval (philosophy #1, axiom #3). Executed-but-unapproved is a valid,
   allowed state.
2. **Can governance reject valid execution observations?** **Yes** — governance may
   withhold acceptance or route to rework. This changes *governance truth* only; it
   does **not** erase the execution truth or the lineage that the work occurred.
3. **Can analytics disagree with operational reports?** **Yes** — analytics may flag a
   report as anomalous, but analytics are advisory (lowest precedence) and may not
   override reports. Both coexist; a human reconciles.
4. **Can contradictory truths coexist temporarily?** **Yes** — this is the normal,
   expected behavior (philosophy #8). Condition: the contradiction is surfaced and
   attributed.
5. **Which truth layer owns progress?** **Execution truth**, owned solely by
   `ProgressService` (derived). Not governance, not reporting, not the client.
6. **Which truth layer owns readiness?** Authoritatively, the **derived interpretation
   layer** — readiness should be *derived* from execution + governance + structural +
   resource facts, not declared by any single actor. It is **not** governance truth.
   **Today it has no owner** (broken `ready` boolean — A4); that is the gap.
7. **Can evidence override human declaration?** **Authoritatively yes** — corroborated
   evidence outranks bare declaration (philosophy #1/#2). But "override" means *evidence
   is the basis on which a human/governance act reconciles*, not that the system
   auto-mutates. **Today declarations are largely trusted** (client-supplied
   status/progress/ready/approved_by — A18), so evidence does **not** currently override
   — a stabilization gap.
8. **Can unresolved contradiction exist operationally?** **Yes** — permitted and
   expected, provided it is **visible and audited**. Forbidden are *silent* unresolved
   contradiction and *automatic* resolution.

---

## 11. Future Runtime Stabilization Implications

The deltas between these semantics and the runtime — stated as boundaries, **not built
here**. Each strengthens an existing owner; none requires a conflict engine or AI.

1. **Surface contradictions instead of hiding them.** A read-side view that shows
   execution-vs-governance and cache-vs-recompute disagreements (no resolution logic).
2. **Make governance consult friction before acceptance** — block `APPROVED` over an
   open disqualifying blocker / without inspection precedence (A5/A15). Owner:
   `WorkflowGovernanceService`.
3. **Define progress as recompute-authoritative; treat the cache as cache** with a
   stated invalidation contract (A3). Owner: `ProgressService`.
4. **Reconcile the three definitions of "done"** (`COMPLETED` / `APPROVED` /
   `progress=100`) into one queryable relationship (A17) before any forecasting trusts
   "done."
5. **Server-derive reconciliation attribution** (replace client `approved_by`) so every
   authority act is trustworthy (A18).
6. **Derive readiness** so it can participate in reconciliation instead of being an
   unowned static flag (A4).
7. **Thread reconciliation causality** through the event ledger
   (`causality_reference`) so lineage shows conflict → resolution.

Each is enforceable within current service ownership. Stabilizing the *meaning* first
ensures that when these are built, they reconcile truth the way the philosophy already
demands — and never let one layer silently overwrite another.

---

## 12. Bottom line

BetavanX already separates the layers that matter — structural, execution, reporting,
governance, lineage, and analytical — and `truth-contracts.md` already gives each
authoritative field exactly one writer. What it has **not** done is make conflict
*visible and governed*. Authoritatively: **reality (execution) is believed over
acceptance (governance); governance validates but never rewrites reality; reporting is
evidence, not verdict; analytics are advisory and mutate nothing; contradictions may
persist as long as they are surfaced and attributed; and reconciliation is always a
human/governance authority act recorded in immutable lineage — never an automatic
resolution.** The runtime honors the ownership rules but currently lets dangerous
contradictions (approval over blockers, stale progress, unowned readiness, trusted
declarations) sit silently. Naming how truth behaves under conflict is what lets those
be closed later without inventing arbitration machinery the platform explicitly does
not want.

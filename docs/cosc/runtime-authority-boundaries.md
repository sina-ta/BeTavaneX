# COSC — Operational Runtime Authority Boundaries

> Who — which layers, actors, services, and semantic systems — is allowed to
> **mutate, interpret, validate, derive, or observe** operational reality, and how.
> This is the capstone that consolidates the authority rules implied across the prior
> stabilization docs into one boundary contract.
>
> **Semantic authority definition only.** No RBAC redesign, no policy engine, no
> authorization framework, no AI governance, no runtime/orchestration redesign. This
> describes *who may affect reality and how* — not how software enforces it. Where the
> runtime diverges, the gap is marked (**Gap**).

## Grounding

Built on: `operational-philosophy.md` (authority model + #9 AI advisory + #10
intelligence-from-semantics), `core-operational-decisions.md` (axioms),
`truth-contracts.md` (one-writer-per-field), `truth-reconciliation-semantics.md`
(precedence), `lifecycle-semantics-stabilization.md` (completion ownership),
`dependency-semantics-stabilization.md` (dependency authority),
`reality-confidence-semantics.md` (confidence is never authoritative), `event-taxonomy.md`
+ `event-ledger-foundation.md` (lineage is append-only), `operational-assumption-registry.md`.

The two governing rules everything below derives from:
- **One writer per authoritative field** (`truth-contracts.md`): a layer *owns* a fact;
  no other layer may write it.
- **Reality precedes and is separate from governance** (axiom #3): execution truth is
  validated by governance, never created or rewritten by it.

---

## 1. Runtime Authority Layer Model

Ten authority layers. Each is defined by **scope · ownership · mutation rights ·
interpretation rights · validation rights · reconciliation rights.**

### 1.1 Structural authority
- **Scope.** Existence, uniqueness, identity, referential integrity.
- **Ownership.** PostgreSQL constraints + `integrity/delete_policy`.
- **Mutation.** Admits/rejects rows; blocks invalid deletes. **Cannot** interpret.
- **Interpretation.** None.
- **Validation.** Hard invariants only (FKs, unique, CHECK value sets).
- **Reconciliation.** None — structural conflicts are *prevented*, never reconciled.

### 1.2 Planning authority
- **Scope.** Intent: Project, WBS, Location, BOQ, ActivityInstance, WorkflowStep
  creation.
- **Ownership.** `PlanningUseCases` (admin/supervisor).
- **Mutation.** Writes **planning truth** (the frame). Yields to execution reality
  (philosophy #1).
- **Interpretation.** None (intent declaration, not interpretation).
- **Validation.** Structural validity of plans.
- **Reconciliation.** May revise plans; cannot rewrite execution/governance truth.

### 1.3 Execution authority
- **Scope.** Field reality: commitments (`WorkOrder`, `execution_weight`), assignment
  links, daily reports, and **derived progress**.
- **Ownership.** `WorkflowExecutionService` (links/reports), callers (work-order
  status), `ProgressService` (progress derivation). Workers contribute observations.
- **Mutation.** Writes **execution truth**; `ProgressService` *derives* (never
  declares) progress.
- **Interpretation.** Progress derivation is computation, not interpretation.
- **Validation.** None of acceptance — execution does not approve itself.
- **Reconciliation.** Progress reconciles by **recomputation**; commitment corrections
  via the two deletable junctions + a reconciliation record.

### 1.4 Governance authority
- **Scope.** Acceptance: approval, inspection reaction, rework, blocker resolution.
- **Ownership.** `WorkflowGovernanceService` (admin/supervisor).
- **Mutation.** Writes **governance truth** (acceptance/status). **Validates** execution;
  **never rewrites** it (axiom #3).
- **Interpretation.** Judges execution against evidence/governance rules.
- **Validation.** The validation layer.
- **Reconciliation.** Reconciles execution-vs-governance contradictions by **forward
  acts** (approve / return-to-rework / resolve), never by editing history.

### 1.5 Coordination authority
- **Scope.** Binding work to steps (link) + role handoff interpretation.
- **Ownership.** `WorkflowExecutionService` (link, Hard); coordination analytics
  (handoff, Observed).
- **Mutation.** Link create/remove (admits/withdraws weight). Handoff: none.
- **Interpretation.** Handoff friction signals (advisory).
- **Validation.** Duplicate-link guard.
- **Reconciliation.** None — coordination informs humans; it does not act.

### 1.6 Observational / reporting authority
- **Scope.** Field observations (daily reports) and activity records.
- **Ownership.** Workers/supervisors (submit); `WorkflowExecutionService` (persist);
  audit/usage stores (record).
- **Mutation.** Appends observations — **not** authoritative truth on its own
  (philosophy #2).
- **Interpretation.** None (raw observation).
- **Validation.** None — a report is evidence, not a verdict.
- **Reconciliation.** Feeds reconciliation as evidence; performs none.

### 1.7 Analytical authority
- **Scope.** Signals, health bands, decision queues, coordination bands.
- **Ownership.** Analytics services (read-only leaves).
- **Mutation.** **None — ever.** Writes no domain state.
- **Interpretation.** Infers/ranks/surfaces — always advisory, lowest precedence.
- **Validation.** None (may *flag*, never *decide*).
- **Reconciliation.** **Surfaces** contradictions; resolves none.

### 1.8 Lineage authority
- **Scope.** The immutable record of what happened (event ledger, audit/usage JSONL).
- **Ownership.** `EventRecordingService` (ledger, append-only); audit/usage stores.
- **Mutation.** **Append-only.** Never updates or deletes a record.
- **Interpretation.** None (records facts/acts; interpretation reads from it).
- **Validation.** None.
- **Reconciliation.** Holds conflict and resolution side by side; reconciles nothing
  itself.

### 1.9 Confidence interpretation authority
- **Scope.** Qualitative trustworthiness of claims (`reality-confidence-semantics.md`).
- **Ownership.** **No single owner; never authoritative state.** Read by the
  analytics/interpretation layer; informed by governance corroboration + lineage.
- **Mutation.** None — confidence is never stored as truth.
- **Interpretation.** Its entire purpose — advisory only.
- **Validation.** None.
- **Reconciliation.** Informs how seriously a contradiction is taken; decides nothing.

### 1.10 AI advisory authority
- **Scope.** Observe, interpret, summarize, recommend (philosophy #9).
- **Ownership.** AI layer (advisory).
- **Mutation.** **None — ever.** AI is never a writer of any field.
- **Interpretation.** May interpret/summarize, including contradictions and confidence.
- **Validation.** None — AI never validates or accepts.
- **Reconciliation.** May *propose* a reconciliation; a human authority performs it.

---

## 2. Mutation Authority Matrix

| Capability | Who holds it | Who explicitly does NOT |
|---|---|---|
| **Mutate planning truth** | Planning (`PlanningUseCases`) | execution, governance, analytics, AI |
| **Mutate execution truth** (commitments/links/reports) | Execution (`WorkflowExecutionService`, callers) | governance, analytics, AI |
| **Derive progress** | Execution (`ProgressService`, compute-only) | anyone declaring a number |
| **Mutate governance truth** (acceptance/status) | Governance (`WorkflowGovernanceService`) | execution, planning, analytics, AI |
| **Validate / accept** | Governance (admin/supervisor) | workers, analytics, AI |
| **Observe / report** | Workers/supervisors | analytics (it interprets, not observes), AI |
| **Interpret / infer** | Analytics, confidence layer, AI | — (but they mutate nothing) |
| **Record lineage** | Lineage (`EventRecordingService`, audit/usage) | anyone editing a past record |
| **Overwrite history** | **Nobody** | every layer |

The matrix is the one-writer rule made explicit. **Reading is universal; writing a
field is owned by exactly one layer; history is owned by no one.**

---

## 3. Governance Authority Rules

1. **Governance validates execution; it does not create it** (axiom #3). Approval means
   "accepted," never "physically done."
2. **Governance cannot redefine execution truth.** It may withhold acceptance of a 100%
   step or accept a 0% one — both leave execution truth intact and surfaced as
   contradiction.
3. **Governance vs execution boundary:** governance writes acceptance/status; execution
   writes commitments/progress. Neither writes the other's fields.
4. **Governance vs historical lineage boundary:** governance acts **append** new
   records (approval, rework, resolution); they **never edit or delete** prior lineage.
   A reversal is a new act referencing the old (`causality_reference`).
5. **Governance authority is role-bounded** (admin/supervisor — `lifecycle-semantics.md`);
   workers observe, they do not govern (philosophy authority model).
6. **Governance should consult execution reality** (readiness, blockers, inspection)
   before accepting — authoritative intent; **Gap** today (A5/A15): approval is
   bypassable.

---

## 4. Analytical Authority Rules

1. **Analytics may infer** signals, bands, queues, coordination interpretations — all
   advisory.
2. **Analytics may never claim truth.** Outputs carry `false_positive_notes` and return
   `data_available: false` without the DB — they are interpretations, not facts
   (`truth-contracts.md`, `event-taxonomy.md`).
3. **Analytics vs operational truth:** lowest precedence. Analytics may *disagree with*
   reports/state and *surface* the discrepancy; they may **never override** it.
4. **Advisory vs authoritative interpretation:** an interpretation is authoritative only
   when a human authority acts on it through the proper mutation layer. The analytic
   output itself is never authoritative.
5. **Analytics write no state** — not progress, not status, not readiness, nothing. They
   are read-only leaves.
6. **Analytics must not infer non-existent states as fact** (e.g. `PENDING` approvals the
   write path never creates — invalid pattern #8): such inferences are low-confidence and
   must be marked, not asserted.

---

## 5. AI Advisory Boundaries

Per philosophy #9 ("AI is advisory, not authoritative") and #10 (intelligence from
semantics, not heuristic theater):

| AI may | AI may never |
|---|---|
| Observe operational state (read) | Mutate any field |
| Summarize execution/governance/lineage | Decide acceptance or completion |
| Interpret contradictions and confidence | Resolve a contradiction itself |
| Recommend governance/execution actions | Perform a governance/execution act |
| Rank/prioritize advisorily | Auto-gate execution or governance |
| Explain derived values | Become the authority of operational truth |

Authoritative AI rules:
1. **AI vs governance:** AI may *recommend* an approval/rework; only a human governance
   authority may *perform* it. AI is never in the write path.
2. **AI vs operational truth:** AI reads and interprets; it never writes truth, and its
   interpretations are advisory (lowest precedence with analytics).
3. **AI vs execution authority:** AI never assigns, completes, or reports on behalf of
   execution — execution reality must originate from real actors/commitments.
4. **AI interpretation must remain explainable and auditable** (philosophy #9) — no
   opaque authority.

---

## 6. Historical Lineage Authority

1. **Lineage is append-only and immutable** (`event-ledger-foundation.md`). No layer —
   not even governance or admin — edits or deletes a past record.
2. **Correction vs deletion:** a mistake is corrected by **appending a corrective act**
   (a new state/event referencing the original), never by erasing the original. Failure
   ≠ deletion (`lifecycle-semantics-stabilization.md` §9).
3. **Audit permanence:** all governance acts, completions (execution + governance), and
   regressions remain auditable forever.
4. **Historical reinterpretation boundary:** *interpretation* of history may evolve
   (analytics/confidence/AI may read old lineage differently over time), but the
   **recorded facts never change.** Reinterpreting is allowed; rewriting is not.
5. **Deletable junctions are the exception that proves the rule:** even though
   `WorkOrderWorkflowStep`/`BOQMapping` rows are removable, their assignment/removal
   *events* persist in lineage — the record outlives the row.
6. **Historical correction authority** belongs to the relevant **mutation layer acting
   forward** (governance for acceptance corrections; execution for commitment
   corrections) — the lineage layer itself corrects nothing.

---

## 7. Forbidden Authority Violations

Crossings that violate the boundary contract. Some are currently *possible* in the
runtime (**Gap**); listed so they can be guarded later without redesign.

1. **Governance overwriting execution history** — editing/erasing what was executed.
   *Forbidden absolutely.*
2. **Analytics or AI writing domain state** — any mutation by a read-only/advisory
   layer. *Forbidden absolutely.*
3. **AI auto-deciding** — performing a governance/execution act, or auto-gating.
   *Forbidden absolutely.*
4. **Direct readiness mutation** — setting `ready` as a free value instead of deriving
   it (A4). *Forbidden authoritatively; **Gap** — runtime allows it.*
5. **Derived overwriting observed/authoritative** — a cached/derived value (progress
   cache) treated as primary over its recomputation or over observed reality (A3).
   *Forbidden.*
6. **Cross-layer field writes (one-writer violation)** — any service writing a field it
   does not own. *Forbidden.*
7. **Silent authority escalation** — a router/service performing a higher-authority
   mutation without it being an explicit, attributed authority act (e.g. client-supplied
   `approved_by` letting attribution be fabricated — A18). *Forbidden authoritatively;
   **Gap**.*
8. **Structural escalation** — cross-project links/allocations breaking aggregate
   integrity (invalid patterns #1/#2). *Forbidden; **Gap**.*
9. **Confidence as authority** — storing/acting on confidence as if it were truth
   (A10). *Forbidden.*
10. **Lineage editing** — updating/deleting any audit or ledger record. *Forbidden
    absolutely.*

---

## 8. Runtime Integrity Expectations

1. **Read is universal; write is owned; history is no one's to edit.** This single
   sentence is runtime integrity.
2. **Every mutation is an attributed authority act** routed through its owning layer —
   never a side effect of analytics/AI/interpretation.
3. **Execution truth and governance truth stay separate** and are reconciled by forward
   acts, not overwrites.
4. **Derived and advisory layers stay subordinate** — they interpret and surface;
   they never decide or write.
5. **Contradictions and uncertainty stay visible** (reconciliation §9, confidence §9) —
   integrity includes not hiding conflict.
6. **The semantic core constrains intelligence** (philosophy #10): no analytics/AI layer
   may exceed its advisory boundary regardless of how "smart" it becomes.

---

## 9. Governance & Audit Expectations

1. **Authority acts are attributed and auditable** — who mutated/validated/accepted,
   when, on what basis. Attribution must be **server-derived**, not client-supplied
   (A18, **Gap**).
2. **Crossing a boundary requires an explicit authority act**, recorded in lineage —
   never an implicit or silent escalation.
3. **Analytics/AI outputs are never recorded as authority acts** — they carry their
   advisory/uncertainty markers (`false_positive_notes`, `data_available`).
4. **Audit captures the evidence available at the time of an act** so later
   reinterpretation cannot retroactively launder a weak decision.
5. **Boundary violations should be detectable** in audit (e.g. a write by a non-owning
   layer is an integrity incident) — observation, not auto-enforcement.

---

## 10. Resolved Questions

1. **Can governance overwrite execution history?** **No.** Governance changes acceptance
   via forward acts; it never edits or deletes execution records or lineage (axiom #3,
   append-only).
2. **Can analytics redefine operational truth?** **No.** Analytics are read-only,
   lowest-precedence interpreters; they surface discrepancies, mutate nothing.
3. **Can AI interpret contradictions?** **Yes** — AI may interpret, summarize, and
   surface contradictions (advisory). It may **not** resolve them.
4. **Can AI recommend governance actions?** **Yes — recommend only.** A human governance
   authority must perform the act; AI is never in the write path.
5. **Can readiness be mutated directly?** **Authoritatively no** — readiness is derived,
   not set. Direct mutation violates the derivation contract (current runtime allows it —
   **Gap**, A4).
6. **Can derived truth overwrite observed truth?** **No.** Derived values (progress
   cache, analytics) never override observed/authoritative truth; derived ≠ primary
   (`truth-contracts.md`).
7. **Which layer owns operational completion?** Depends which completion: **execution
   authority** owns execution completion (`ProgressService` derivation from
   `WorkOrder.COMPLETED`); **governance authority** owns governance completion
   (`APPROVED`). There is no single "completion" owner (`lifecycle-semantics-stabilization.md`
   §5).
8. **Who owns historical correction authority?** **No one may edit history.** Correction
   is the right to **append a corrective act**, owned by the relevant mutation layer
   acting forward (governance for acceptance, execution for commitments). The lineage
   layer itself corrects nothing.

---

## 11. Future Runtime Stabilization Implications

Deltas between this contract and the runtime — **boundaries, not built here**, each
strengthening an existing owner; none requires RBAC redesign or a policy engine.

1. **Server-derive attribution** for every authority act (replace client `approved_by`)
   so no silent escalation is possible (A18, violation #7).
2. **Give readiness a single deriver** so direct mutation stops being a legal write
   (A4, violation #4).
3. **Enforce same-project edge integrity** on links/allocations (violation #8, invalid
   patterns #1/#2).
4. **Keep progress recompute-authoritative** so the cache can never overwrite derived
   truth (A3, violation #5).
5. **Make governance consult execution reality** before acceptance (A5/A15) — within
   `WorkflowGovernanceService`.
6. **Mark analytics/AI outputs as advisory at the boundary** so no consumer mistakes an
   interpretation for an authority act.
7. **Treat non-owning writes as integrity incidents** in audit — observation only.

Each lives within current service ownership. Stabilizing *who may affect reality and
how* first ensures that when enforcement is added it hardens the existing one-writer
boundaries — and never lets analytics, AI, a cache, or a rubber-stamp quietly assume
authority it was never granted.

---

## 12. Bottom line

BetavanX already has the bones of clean authority: `truth-contracts.md` assigns one
writer per field, analytics are read-only leaves, and the philosophy keeps AI advisory.
What this document fixes is the **whole boundary contract in one place**: structural and
mutation layers *write* (each its own field), governance *validates* without rewriting
reality, execution and planning *own their truths*, analytics/confidence/AI *interpret
and recommend but never decide or mutate*, and lineage is *append-only and editable by
no one*. The integrity rule reduces to one sentence — **read is universal, writing is
owned, history is no one's to edit** — and the current gaps (client-supplied
attribution, unowned readiness, cross-project links, trusted cache, bypassable
approval) are exactly the places where authority can silently leak across a boundary.
Naming the boundaries now is what lets those leaks be closed later without inventing a
permission framework the platform explicitly does not want.

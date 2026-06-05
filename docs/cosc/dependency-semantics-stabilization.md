# COSC — Dependency Semantics Stabilization

> This document fixes the **authoritative operational meaning** of each dependency
> type in BetavanX: what it is allowed to mean, what it may block, what it may
> propagate, and what it must never do. It is the *contract*, not the engine.
>
> **Semantic stabilization only.** No graph DB, no scheduler, no propagation system,
> no optimization, no simulation, no runtime redesign. Where the contract and the
> current runtime disagree, the gap is stated explicitly — but nothing is built here.

## Relationship to the other COSC docs

- `dependency-taxonomy.md` answered **"what does the runtime do today?"** (Enforced /
  Declared / Observed).
- This document answers **"what is each dependency *allowed to mean*, authoritatively?"**
- The two are read together as: *authoritative meaning* (here) vs *current
  enforcement* (taxonomy). The delta between them is the stabilization backlog.

Grounded in: `dependency-taxonomy.md`, `operational-philosophy.md`,
`core-operational-decisions.md` (axioms), `operational-assumption-registry.md`,
`execution-physics.md`, `truth-contracts.md`, `lifecycle-semantics.md`.

---

## 0. The authority scale (definitions)

Every dependency is assigned exactly one **authoritative authority level**:

- **Hard** — operationally binding. May block an operation and/or is a source of
  operational truth. Violations are not tolerated, even temporarily.
- **Soft** — a real operational constraint that *should* shape readiness/decisions,
  but may be temporarily violated with the violation made visible. Never silently
  overrides truth.
- **Advisory** — informs humans; carries no power to block or propagate state.
  Temporary violation is normal.
- **Observational** — exists only as interpretation in analytics; changes signals,
  never state, never blocks.

Two independent powers are defined separately from authority level:

- **Blocking authority** — whether the dependency may *prevent* an operation.
- **Propagation authority** — whether the dependency may *push state* to other
  entities.

A dependency can be Hard for truth yet have **no** blocking authority (e.g.
execution/progress is authoritative truth but blocks nothing).

---

## 1. Dependency Authority Matrix

| Dependency | Authoritative authority | Blocking authority | Propagation authority | Readiness impact | Governance impact | Truth class | Runtime status today |
|---|---|---|---|---|---|---|---|
| `containment_dependency` | **Hard** | Delete-time only | Delete cascade/restrict | None | None | Structural truth | **Matches** (enforced) |
| `spatial_dependency` (existence/uniqueness) | **Hard** | Create-time only | None | Precondition (existence) | None | Structural truth | **Matches** (enforced) |
| `spatial_dependency` (sequencing) | **Soft** (intended) | None | None | Yes (intended) | None | — | **Absent** (no edges) |
| `execution_dependency` | **Hard** (truth) | **None** | Pull, bottom-up | Evidence of capability | None | **Operational truth** | Partial (unweighted, cache gap) |
| `coordination_dependency` (link) | **Hard** | Duplicate-block | Enables weight | Precondition (existence) | None | Structural truth | **Matches** (enforced) |
| `coordination_dependency` (handoff) | **Advisory** | None | Signal only | Informs | Informs | Coordination signal | **Matches** (observed) |
| `governance_dependency` | **Hard** (acceptance) | **State transition only** | Step status only | None (validates, not enables) | **Owns** acceptance | **Governance truth** | Partial (bypassable) |
| `readiness_dependency` | **Soft** (derived, composite) | None (gate is advisory) | None | **Is** the readiness verdict | Input to governance | Derived interpretation | **Broken** (unowned boolean) |
| `resource_dependency` | **Soft** (constrains readiness) | None | None | Yes (intended) | None | Operational constraint | **Declared** (descriptive only) |
| `informational_dependency` | **Observational** | None | Signal only | Informs | Informs | Interpretation | **Matches** (observed) |

> Reading the matrix: only **containment, spatial-existence, coordination-link, and
> governance** may ever block. Only **execution, governance, containment, and
> coordination-link** may propagate. Everything else is soft/advisory/observational
> by authoritative design — and `readiness`/`resource` are the two dependencies whose
> *authoritative* soft constraint the runtime currently fails to honor.

---

## 2. Authoritative definitions (per dependency)

Each defines the 12 stabilized properties. "**Gap**" marks where the runtime does
not currently honor the authoritative meaning (no fix here).

### 2.1 `containment_dependency` — Hard (structural)
1. **Operational meaning.** Operational data exists only inside its parent (the
   planning-hierarchy spine).
2. **Authority level.** Hard.
3. **Blocking authority.** Blocks **deletion** of a parent with children; never
   blocks execution.
4. **Propagation authority.** Delete-time only (`RESTRICT` / `CASCADE` / `SET NULL`).
5. **Readiness impact.** None (existence is assumed, not a readiness factor).
6. **Governance impact.** None.
7. **Timeline impact.** Enforces top-down creation order; no runtime time effect.
8. **Coordination impact.** None.
9. **Failure semantics.** A missing parent makes the child non-existent, not
   "failed." There is no partial containment.
10. **Contradiction semantics.** Cannot contradict — it is a structural invariant.
11. **Lifecycle interaction.** Why lifecycles terminate in *status*, not deletion.
12. **Event lineage expectations.** Creation/membership changes are the natural
    lineage anchors (parent context on every event via `aggregate_id`/project).

### 2.2 `spatial_dependency` — Hard (existence) / Soft (sequencing, intended)
1. **Operational meaning.** Work is located: ActivityInstance = WBS×Location,
   unique. Existence of the location is mandatory; spatial **sequencing** ("floor 1
   before floor 2") is operationally real but **not modeled**.
2. **Authority level.** Existence/uniqueness = Hard; sequencing = Soft (intended,
   absent).
3. **Blocking authority.** Existence blocks **creation** of a misplaced/duplicate
   activity. Sequencing blocks nothing (no edges).
4. **Propagation authority.** None at runtime.
5. **Readiness impact.** Spatial access is an **authoritative readiness factor**
   (philosophy #6: "spatial access"). **Gap:** not computed.
6. **Governance impact.** None.
7. **Timeline impact.** None today; spatial sequencing would be a timeline input if
   it existed.
8. **Coordination impact.** Spatial congestion/trade-stacking is a real coordination
   factor — **absent** (`execution-physics.md` §3.3).
9. **Failure semantics.** Missing/closed location → activity cannot be validly
   created; closing a location does **not** cascade to its activities (Gap).
10. **Contradiction semantics.** None for existence; sequencing contradictions cannot
    arise because they cannot be expressed.
11. **Lifecycle interaction.** Location has its own `ACTIVE → CLOSED`, decoupled from
    activity lifecycles (Gap).
12. **Event lineage expectations.** Location context belongs in event metadata so
    spatial analysis is later possible without new state.

### 2.3 `execution_dependency` — Hard (operational truth), non-blocking
1. **Operational meaning.** A step's realized progress depends on completion of the
   work orders committed to it (`execution_weight`, `WO.status == COMPLETED`).
2. **Authority level.** Hard **for truth** — this is the authoritative source of
   *progress*. (Axiom #4: progress is derived, not declared.)
3. **Blocking authority.** **None.** Progress measures; it never gates. Low progress
   blocks nothing.
4. **Propagation authority.** Pull, bottom-up: step → activity → project. Authoritative
   roll-up should be **weighted**; runtime is unweighted (**Gap**, A1).
5. **Readiness impact.** Completed predecessors are an authoritative readiness factor;
   but there is no predecessor network, so execution informs readiness only as
   "evidence of capability," not as a computed prerequisite (Gap, A11).
6. **Governance impact.** None — progress and approval are independent truths.
7. **Timeline impact.** Progress moves only on completion events; authoritative intent
   is that real start/finish timing is captured in lineage (Gap: time inert, A6).
8. **Coordination impact.** Coordination links are what feed execution; removing a
   link withdraws its weight.
9. **Failure semantics.** A reverted/never-completed work order silently changes the
   denominator with no reconciliation event (Gap, invalid pattern #7).
10. **Contradiction semantics.** `progress = 100` may contradict `status ≠ APPROVED`;
    this contradiction is **allowed to exist** (layered truth) but must be surfaced,
    never auto-resolved (A17).
11. **Lifecycle interaction.** Independent of status by design — progress is execution
    truth, status is governance truth.
12. **Event lineage expectations.** Each completion that changes progress should be
    traceable to a work-order completion event (the ledger is the substrate).

### 2.4 `coordination_dependency` — Hard (link) / Advisory (handoff)
1. **Operational meaning.** (a) Link: a work order is bound to a step (the unit of
   field coordination). (b) Handoff: role→role dependencies (report→approval,
   assignment→reporting).
2. **Authority level.** Link = Hard; handoff = Advisory.
3. **Blocking authority.** Link blocks **duplicate** assignment. Handoff blocks
   nothing — and **must not** (human coordination, not automation).
4. **Propagation authority.** Link enables a work order's weight to enter the step's
   progress formula. Handoff propagates into coordination signals only.
5. **Readiness impact.** Coordination resolution is an authoritative readiness factor
   (philosophy #6); today it informs, never computes (Gap).
6. **Governance impact.** None directly; handoff imbalance *informs* governance load.
7. **Timeline impact.** Handoff gaps are time-windowed signals; no state effect.
8. **Coordination impact.** This *is* the coordination dependency. Authoritatively,
   coordination friction is real but **advisory** — it never auto-acts.
9. **Failure semantics.** A broken link (deleted) cleanly withdraws weight. A handoff
   gap degrades a coordination band; nothing fails operationally.
10. **Contradiction semantics.** A link can validly exist while handoff signals say
    "stressed"; no contradiction — different layers.
11. **Lifecycle interaction.** The link is one of two **deletable** carriers
    (correctable). Handoffs read live statuses, change none.
12. **Event lineage expectations.** Assignment is a recorded ledger event
    (`work_order_assigned`); handoff intelligence may later read lineage instead of
    audit-text (Gap, A12).

### 2.5 `governance_dependency` — Hard (acceptance authority), bypassable today
1. **Operational meaning.** A step's authoritative *acceptance* depends on a
   governance act (approval; inspection outcome).
2. **Authority level.** Hard — governance owns the acceptance verdict. **But
   governance is not reality** (axiom #3): it validates, it does not create execution.
3. **Blocking authority.** Blocks **state transitions** (acceptance/advancement of
   authority state), **not** the physical act of execution. Approving cannot make work
   happen; refusing approval cannot un-happen executed work.
4. **Propagation authority.** Propagates to **step status only** (`APPROVED`). Does
   **not** cascade to activity/project status (and authoritatively should not, absent
   a defined roll-up).
5. **Readiness impact.** Governance requirements are an authoritative readiness factor
   (philosophy #6). Authoritatively, governance *consults* readiness/blockers before
   acceptance; **Gap:** it consults neither (A15).
6. **Governance impact.** It is the governance authority.
7. **Timeline impact.** Occurs after execution by convention; not time-enforced.
8. **Coordination impact.** Approval backlog is a coordination signal (advisory).
9. **Failure semantics.** A rejected inspection routes to rework; an over-approval
   (duplicate) is blocked. Authoritative intent: approval over an open CRITICAL blocker
   or without inspection is **invalid**; runtime allows it (Gap, A5/A15, invalid
   pattern #4).
10. **Contradiction semantics.** Governance truth (`APPROVED`) may temporarily
    contradict execution truth (`progress < 100`) or an open blocker. Allowed to
    exist, must be surfaced; governance **may not** overwrite execution truth and
    execution **may not** overwrite governance truth.
11. **Lifecycle interaction.** Owns step status transitions; shares the `APPROVED`
    target with inspection-pass (two origins, one state — A-side of F-cluster).
12. **Event lineage expectations.** Approval is a recorded ledger event
    (`approval_completed`); attribution should be server-derived, not client-supplied
    (Gap, A18).

### 2.6 `readiness_dependency` — Soft (derived, composite), currently broken
1. **Operational meaning.** "Execution can safely and realistically proceed"
   (philosophy #6) — a **composite verdict** over predecessors, governance, resources,
   spatial access, crew, and coordination.
2. **Authority level.** Soft. Authoritatively, readiness is **derived**, never
   declared, and is a *recommendation to proceed*, not a hard gate.
3. **Blocking authority.** None (advisory). Authoritatively it should *warn* before
   work on an unready step, not forbid it (reality may precede readiness, like axiom
   #3 for approval).
4. **Propagation authority.** None. Readiness is **not inherited** automatically (see
   Q: "Is readiness inherited?" — No). Each step's readiness is its own verdict.
5. **Readiness impact.** It **is** readiness.
6. **Governance impact.** An authoritative *input* to governance acceptance, not a
   product of it.
7. **Timeline impact.** Encodes no time today; would consume predecessor timing if a
   network existed.
8. **Coordination impact.** Coordination resolution is one of its component factors.
9. **Failure semantics.** A "ready" step that is actually blocked is a **false
   positive** — the most operationally dangerous readiness failure.
10. **Contradiction semantics.** `ready = true` with an open blocker is a contradiction
    that **must be surfaced**; authoritatively, an open blocker forces readiness toward
    "not ready."
11. **Lifecycle interaction.** Should track changes in its component factors; today it
    is a static creation-time boolean disconnected from everything (Gap, A4).
12. **Event lineage expectations.** Readiness *changes* (became ready / lost
    readiness) are future lineage candidates; none recorded today.

### 2.7 `resource_dependency` — Soft (constrains readiness), descriptive today
1. **Operational meaning.** Steps depend on materials/permits/documents/crew to be
   executable, and on BOQ allocation to be costable.
2. **Authority level.** Soft — resource shortfalls *should* lower readiness, not hard-
   block execution.
3. **Blocking authority.** None today; authoritatively it never *hard*-blocks but is a
   readiness input.
4. **Propagation authority.** None.
5. **Readiness impact.** Material/crew availability is an authoritative readiness
   factor (philosophy #6). **Gap:** resources are descriptive text/counts (A19).
6. **Governance impact.** Missing permits *should* be an acceptance concern; not
   enforced.
7. **Timeline impact.** None encoded; no rate/throughput (A8).
8. **Coordination impact.** Resource contention is a real coordination factor —
   absent.
9. **Failure semantics.** A missing required permit/resource produces no operational
   effect today; authoritatively it should degrade readiness.
10. **Contradiction semantics.** "Required permit absent" + "step approved" is a
    contradiction the runtime cannot currently detect.
11. **Lifecycle interaction.** `BOQMapping` is the second deletable carrier; template
    archival does not invalidate referencing steps (Gap).
12. **Event lineage expectations.** Resource consumption/availability events are out of
    scope today; BOQ is planned-only (no actuals/earned value).

### 2.8 `informational_dependency` — Observational
1. **Operational meaning.** Interpretation depends on evidence and logs (daily
   reports, audit ledger, usage, operational events).
2. **Authority level.** Observational.
3. **Blocking authority.** None — ever. Missing information lowers a score; it never
   blocks.
4. **Propagation authority.** Into **signals** only; one-way; never returns to state.
5. **Readiness impact.** Informs readiness interpretation; does not set it.
6. **Governance impact.** Informs governance load; does not gate.
7. **Timeline impact.** Heavily time-windowed (`OPS_*` thresholds).
8. **Coordination impact.** Source of coordination bands (advisory).
9. **Failure semantics.** Stale/missing evidence → degraded signal, not failure.
10. **Contradiction semantics.** May infer states the runtime never produces (e.g.
    `PENDING` approvals) — an informational dependency on an unreachable state (Gap,
    invalid pattern #8).
11. **Lifecycle interaction.** Reads many lifecycles, changes none.
12. **Event lineage expectations.** The ledger is its preferred future source over
    audit-text mining.

---

## 3. Blocking Semantics

Authoritative rule: **only four dependencies may block, and each blocks a different
thing.**

| Dependency | What it may block | What it may NOT block |
|---|---|---|
| `containment` | Deletion of a parent with children | Execution, acceptance |
| `spatial` (existence) | Creation of a misplaced/duplicate activity | Execution based on neighbors |
| `coordination` (link) | Duplicate assignment | Execution, acceptance |
| `governance` | **State transitions** (acceptance/advancement) | The physical act of execution |

Everything else (`execution`, `readiness`, `resource`, coordination-handoff,
`informational`) **has no blocking authority**. Progress does not block; readiness
warns but does not forbid; resources and information never block.

**Authoritative principle (from axiom #3):** *governance blocks acceptance, not
reality.* Approval can refuse to validate executed work; it cannot prevent the work
from physically occurring, and reality may legitimately exist ahead of governance.

---

## 4. Propagation Semantics

Authoritative rule: **only four propagation paths exist, all local; nothing cascades
up the planning hierarchy.**

1. **Execution → progress** (pull, bottom-up, *weighted* authoritatively; unweighted
   in runtime — Gap A1). Step → activity → project.
2. **Governance → step status** (direct, local, stops at the step).
3. **Containment → deletion** (restrict up / cascade or re-root down).
4. **Coordination link → execution eligibility** (link admits a work order's weight).

**Must NOT propagate (authoritative):**
- Blockers must not silently propagate to progress or status (they may *inform*
  readiness — see §5).
- Readiness is not inherited.
- Resource/permit/document state does not propagate.
- Status does not cascade up the hierarchy (a completed step does not complete its
  activity/project) unless a roll-up is later defined explicitly.
- Informational signals never return to domain state.

---

## 5. Readiness Semantics

Authoritative definition (philosophy #6, axiom #2): **readiness is a derived,
composite, per-entity verdict** — "execution can safely and realistically proceed" —
not a stored flag and not a schedule status.

Authoritative component factors (all *soft* inputs):
- predecessor completion (execution),
- governance requirements satisfied,
- resource/material/crew availability,
- spatial access,
- coordination resolution,
- absence of disqualifying blockers.

Authoritative rules:
- Readiness is **derived**, never client-declared.
- Readiness is **advisory**: it recommends, it does not hard-gate (reality may precede
  readiness).
- Readiness is **not inherited**; each entity computes its own.
- An open disqualifying blocker forces readiness toward "not ready," and the
  contradiction (`ready=true` + open blocker) must be surfaced.

**Runtime gap:** `WorkflowStep.ready` is a static, unowned, client-set boolean
honoring *none* of the above (A4, taxonomy 2.6). This is the single largest gap
between authoritative meaning and runtime.

---

## 6. Governance Dependency Rules

Authoritative rules for governance acceptance:

1. **Governance validates; it does not create reality** (axiom #3). `APPROVED` means
   "accepted/authorized," not "physically done."
2. Governance acts on **state transitions**, not on execution itself.
3. Governance is the **single owner** of acceptance (`WorkflowGovernanceService`);
   no other layer may set acceptance state.
4. Acceptance **should consult** readiness, blockers, and inspection precedence
   before granting `APPROVED`. *(Authoritative intent; runtime consults none — A15,
   invalid pattern #4. Stated, not fixed.)*
5. Attribution of a governance act should be **server-derived from the actor**, not
   client-supplied (A18).
6. Governance truth and execution truth are **separate layers** (§9); neither
   overwrites the other; conflicts are surfaced, not auto-resolved.
7. Governance propagation stops at the step; no hierarchy cascade is implied.

---

## 7. Coordination Dependency Rules

Authoritative rules:

1. The **link** is structural and Hard: it is the only way a work order's weight
   enters a step; duplicates are blocked; it is correctable (deletable).
2. The **handoff** is Advisory and **must remain advisory** — coordination
   intelligence informs humans; it never auto-assigns, auto-approves, or blocks.
3. Coordination resolution is a **soft readiness factor**, not a gate.
4. Coordination friction is **real but non-authoritative**: it shapes signals and
   human attention, not state.
5. Coordination signals should migrate to event-lineage sources over time rather than
   audit-text mining (A12) — a semantic preference, not a build mandate here.

---

## 8. Failure & Contradiction Semantics

**Contradiction is permitted; silent resolution is not.** Per philosophy #8,
operational truth is *layered* and perspectives may temporarily conflict. The
stabilized rules:

- **Allowed temporary contradictions** (must be surfaced, never auto-resolved):
  - execution truth vs governance truth (`progress=100` vs not `APPROVED`),
  - readiness vs blocker (`ready=true` vs open blocker),
  - reporting vs execution (a report asserting work not reflected in progress).
- **Disallowed contradictions** (structural invariants; must never occur):
  - a child without its parent (containment),
  - two activities at the same WBS×Location (spatial uniqueness),
  - a work order's weight counting in a step from a **different project** (invalid
    pattern #1 — currently *possible*, authoritatively *forbidden*).
- **No dependency may overwrite another layer's truth.** Governance cannot rewrite
  progress; analytics cannot rewrite either; readiness cannot fabricate execution.
- **Failure ≠ deletion.** Operational failure (rework, blocker, failed inspection) is
  a *state*, never row removal; lineage is preserved.

**Temporary violation policy by authority level:**

| Authority | Temporary violation allowed? |
|---|---|
| Hard | No |
| Soft (readiness, resource, governance-precedence) | Yes, if surfaced |
| Advisory (coordination handoff) | Yes (normal) |
| Observational | N/A (cannot be violated) |

---

## 9. Dependency Truth Hierarchy

Which dependencies *are* operational truth, and which are governance/observational
constructs. (Aligned with `truth-contracts.md` and philosophy #8.)

```
STRUCTURAL TRUTH        containment, spatial-existence, coordination-link
   (invariant, DB-owned; cannot be contradicted)
        │
EXECUTION TRUTH         execution_dependency  → progress
   (derived, bottom-up; the "what physically advanced" layer)
        │
GOVERNANCE TRUTH        governance_dependency → acceptance/status
   (validates execution truth; SEPARATE layer; never overwrites it)
        │
DERIVED INTERPRETATION  readiness (composite), resource (constraint)
   (soft; should be derived from the layers above)
        │
OBSERVATIONAL           informational, coordination-handoff
   (signals only; never state)
```

Authoritative ordering principles:
- **Structural and execution truth are operational truth.** They describe reality.
- **Governance truth is a distinct layer**, not reality (axiom #3). It may lag, lead,
  or temporarily conflict with execution truth.
- **Readiness and resource are derived interpretations**, not primary truth — they
  *should* be computed from execution + governance + structural facts.
- **Informational and handoff are observational** — never authoritative.
- **No layer owns all truth** (philosophy #8); reconciliation surfaces conflict, it
  does not collapse layers.

---

## 10. Resolved Questions

Direct answers, authoritatively, grounded in the current model + philosophy:

1. **Can blockers propagate?** Not to progress or status (they are inert there and
   authoritatively must not silently propagate). They **should** act as a *soft*
   readiness constraint and a governance concern. Today: neither (A5). Authoritative
   stance: blocker → readiness (soft) and → governance visibility; never an automatic
   state mutation.
2. **Can approvals block execution?** No. Approval blocks **acceptance/state
   transition**, not the physical act of execution (axiom #3). Reality may precede
   approval.
3. **Is readiness inherited?** No. Readiness is a per-entity derived verdict, not
   propagated from parents or predecessors (there is no predecessor network to inherit
   along).
4. **Are coordination dependencies enforceable?** The **link** is enforceable (and
   enforced). The **handoff** is advisory and must stay advisory — not auto-enforced.
5. **Can dependencies conflict?** Yes, across layers (execution vs governance,
   readiness vs blocker). Conflicts are permitted, must be surfaced, and must never be
   silently resolved by overwriting another layer's truth.
6. **Can dependencies be temporarily violated?** Hard: never. Soft (readiness,
   resource, governance precedence): yes, if the violation is visible. Advisory:
   routinely. Observational: not applicable.
7. **Which dependencies are operational truth?** Structural (containment, spatial-
   existence, coordination-link) and **execution** (progress). These describe reality.
8. **Which are governance constructs only?** `governance_dependency` (approval /
   inspection) — governance truth, explicitly *not* execution reality.

---

## 11. Recommended Future Enforcement Boundaries

Where enforcement *should* eventually live, stated as boundaries — **not built here.**
Each closes a delta between authoritative meaning (this doc) and runtime
(`dependency-taxonomy.md`).

1. **Same-project edge invariants** for `WorkOrderWorkflowStep` and `BOQMapping`
   (close invalid patterns #1/#2). Hard structural truth must not cross aggregates.
2. **Acyclicity guards** on WBS/Location `parent_id` (#3). Structural trees must be
   acyclic.
3. **Single readiness deriver** that owns `ready` from its component factors (§5).
   Until then, `ready` must be documented as a non-authoritative hint, not trusted.
4. **Governance precedence checks** — `APPROVED` should consult inspection, blockers,
   and readiness (§6). Boundary owner: `WorkflowGovernanceService` (no new service).
5. **Server-derived attribution** for governance acts (replace client `approved_by`).
6. **Progress truth contract** — define derived-on-read vs cached-with-invalidation,
   and make roll-up weighted (A1/A3). Owner: `ProgressService` (sole owner).
7. **Blocker → readiness boundary** — an open disqualifying blocker degrades readiness
   (soft), surfaced as a contradiction; blockers still never mutate progress/status.
8. **Completion reconciliation** — one authoritative "done" relating `COMPLETED` /
   `APPROVED` / `progress=100` (A17) before any propagation or forecasting is built.

Each boundary is enforceable *within the existing service ownership* — none requires a
graph DB, scheduler, or new orchestration layer. That is the point of stabilizing the
meaning first: it tells future enforcement exactly where to live and what it must
uphold.

---

## 12. Bottom line

Authoritatively, BetavanX has a clean dependency contract: **structural and execution
dependencies are truth; governance is a separate validating layer; readiness and
resource are soft derived constraints; coordination-handoff and information are
advisory/observational; and only four dependencies may ever block, each a different
thing.** The runtime honors the structural and execution halves, partially honors
governance, and currently fails the soft layer (readiness/resource) by leaving it
declared-but-unowned. Nothing in this document changes the runtime — it fixes the
*meaning* so that when enforcement is eventually added, it strengthens the existing
service owners instead of inventing new machinery, and so that no future intelligence
layer mistakes an advisory constraint for operational truth.

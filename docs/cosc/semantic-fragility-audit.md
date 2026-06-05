# COSC — Semantic Fragility Audit

> Brutally honest, implementation-grounded audit of where BetavanX's operational
> semantics are fragile, ambiguous, or held together by convention rather than by
> the architecture. This is an audit only — no redesign, no features, no API
> changes. Findings reference the real code paths verified during the COSC phase.
>
> Severity scale: **Critical** (wrong operational truth or authority can be
> produced today), **High** (silent inconsistency / data-integrity risk),
> **Medium** (maintenance + drift risk), **Low** (cosmetic / latent).

## Severity summary

| # | Finding | Category | Severity |
|---|---|---|---|
| F1 | Client supplies `approved_by` / `submitted_by`; attribution ≠ authenticated actor | Authority ambiguity | **Critical** |
| F2 | Progress cache (`progress_percent`) is never refreshed automatically | Derived truth ambiguity | **Critical** |
| F3 | Two divergent progress truths exposed on the same data (cached vs live) | Derived truth ambiguity | **High** |
| F4 | `WorkflowStepCreate` lets the client set `status` / `progress_percent` / `ready` freely | Lifecycle fragility | **High** |
| F5 | Two paths to `APPROVED` with different (and one absent) preconditions | Authority + lifecycle | **High** |
| F6 | Status orderings are convention-only (set-only, no transition guard) | Convention-only semantics | **High** |
| F7 | Membership boundary self-erodes via participation grants | Authority ambiguity | **High** |
| F8 | `ready` flag has meaning but no owner — nothing computes it | Convention-only / authority | **Medium** |
| F9 | Blocker severity has no operational effect; only analytics "see" it | Analytics-semantic mismatch | **High** |
| F10 | Analytics infer `PENDING`/`UNDER_REVIEW` approvals the write path never creates | Analytics-semantic mismatch | **High** |
| F11 | `project_id` resolution duplicated across 3+ layers | Semantic duplication | **Medium** |
| F12 | Project-activity enumeration done two different ways (one unbounded) | Semantic duplication + scaling | **High** |
| F13 | `ValueError` overloaded for not-found and rule violation; string-sniffed to 404/409 | Runtime semantic leakage | **High** |
| F14 | Analytics depend on private (`_`-prefixed) functions across modules | Hidden coupling | **Medium** |
| F15 | Threshold/status constant sets duplicated across analytics modules | Semantic duplication | **Medium** |
| F16 | `COMPLETED` vs `APPROVED` workflow-step states have overlapping/unclear meaning | Semantic ambiguity | **Medium** |
| F17 | Optimistic locking is opt-in; default is silent last-write-wins | Lifecycle fragility | **High** |
| F18 | Domain actor UUIDs vs audit username are two unlinked identity systems | Semantic duplication | **Medium** |
| F19 | DailyReport "submit" creates `DRAFT`; status not driven by the verb | Operational terminology | **Medium** |
| F20 | Progress is unweighted while `planned_weight` exists unused | Semantic ambiguity | **Medium** |

---

## 1. Convention-only semantics

### F6 — Status transitions are social, not architectural
**Description.** Every status column except a handful of `WorkflowStep` paths is
**set-only**: the DB `CheckConstraint` validates the *value set*, but nothing
validates *ordering*. `WorkOrder`, `DailyReport`, `Inspection`, `PunchItem`,
`Project`, `WBSItem`, `Location`, `BOQItem`, and most `WorkflowStep` moves can jump
to any legal value from any state. The only real guards are
`mark_inspection_passed` (requires `INSPECTION_PENDING`), the duplicate-approval
and duplicate-assignment checks, and `resolve_blocker`.

**Architectural risk.** The lifecycle diagrams in `lifecycle-semantics.md` describe
intent, not enforcement. Any new caller (or a future endpoint) can violate them
without tripping a single guard.

**Operational consequence.** A work order can be `COMPLETED` then silently moved
back to `CREATED`; an inspection can be `FAILED` while the step is `APPROVED`. The
record set can represent operationally impossible histories.

**Severity:** High.

**Stabilization direction.** Centralize allowed transitions per entity in one
declarative place (a transition table consulted by the owning service) — no schema
or API change, just route status writes through a single validated chokepoint.

### F8 — The `ready` flag means something but nobody owns it
**Description.** `WorkflowStep.ready` is a first-class boolean, is filterable in
the runtime API, and reads as "this step is ready to execute." Yet **no service
computes or flips it.** It is whatever the client passed at creation
(`WorkflowStepCreate.ready`) and never changes.

**Architectural risk.** A queryable operational concept ("readiness") with no
authority behind it. Consumers will assume it's meaningful.

**Operational consequence.** Dashboards/filters on `ready=true` reflect a stale
creation-time guess, not actual readiness. Decisions made on it are unfounded.

**Severity:** Medium.

**Stabilization direction.** Either define a single owner that derives `ready`, or
explicitly document it as "manual hint, not system-derived" in the API contract.
Pick one — today it silently pretends to be derived.

---

## 2. Hidden coupling

### F2 — Progress propagation depends on `WorkOrder.status == COMPLETED`, but nothing recomputes the cache
**Description.** `ProgressService.calculate_workflow_step_progress` counts a work
order's `execution_weight` only when its status is exactly `COMPLETED`. That is the
single hinge of all progress. But `persist_workflow_step_progress` — the only
writer of the cached `workflow_steps.progress_percent` — **is never called** from
any router, use case, or service (verified: it is defined and unreferenced; prior
internal reports already note it "exists but is not surfaced").

**Architectural risk.** A critical truth (progress) is coupled to a status value
that no code path links to a recompute. Marking a work order `COMPLETED` updates
nothing downstream.

**Operational consequence.** The stored `progress_percent` is effectively frozen
at its creation value forever, while the "real" progress drifts. Any consumer
reading the cached field sees fiction.

**Severity:** Critical.

**Stabilization direction.** Decide one model: either treat `progress_percent` as
always-derived (never read the column; always compute) or trigger
`persist_workflow_step_progress` at the WO-completion chokepoint. Right now it is
neither, which is the worst case.

### F7 — Access boundary self-erodes through participation grants
**Description.** Membership is supposed to be the tenancy boundary, but it widens
itself as a side effect of normal work: `register_new_project` grants the creator
**and every investor**; `grant_project_operational_team` (called on every work-order
assignment) grants **every supervisor and worker**; `submit_daily_report` grants
the submitter. After the first assignment, essentially the whole non-admin user
base can access the project.

**Architectural risk.** "Project access control" and "operational convenience" are
fused. The boundary's actual scope is emergent, not declared.

**Operational consequence.** Confidentiality assumptions ("only this team sees this
project") are false in practice. There is no way to have a restricted project once
any work order is assigned.

**Severity:** High.

**Stabilization direction.** Separate "can act" from "auto-granted to act." Make
bulk grants explicit/opt-in rather than a hidden side effect of assignment.

### F14 — Cross-module dependence on private functions
**Description.** `decision_support_service` and `coordination_intelligence_service`
import `_stall_days`, `_approval_delay_days`, `_utc_now`, `_project_id_match`,
`_audit_*`, and constant sets like `_PENDING_APPROVAL` **directly from**
`operational_intelligence_service` (all underscore-private).

**Architectural risk.** The leading-underscore contract ("internal, may change")
is violated by the system itself. Refactoring one analytics file silently breaks
two others.

**Operational consequence.** Low runtime risk today, high change-fragility: a
threshold/semantics tweak in one module mutates the meaning of signals in modules
the author didn't touch.

**Severity:** Medium.

**Stabilization direction.** Promote the shared thresholds/constants/helpers into
one explicitly-public analytics-commons module; stop importing privates.

---

## 3. Semantic duplication

### F11 — `project_id` resolution implemented in multiple layers
**Description.** `get_activity_instance_project_id` (and siblings
`get_work_order_project_id`, `get_workflow_step_project_id`) exist in
`PlanningUseCases`, `RuntimeQueryService`, **and** `RuntimeUseCases`, all doing the
same "walk the resource up to its project" lookup.

**Architectural risk.** The same operational mapping has several homes; they can
diverge (e.g., null-handling differences) and there's no single source for "what
project does this resource belong to."

**Operational consequence.** Access checks depend on this mapping; divergence is a
quiet authorization bug.

**Severity:** Medium.

**Stabilization direction.** One canonical resolver used by both authorization and
queries.

### F12 — Two ways to enumerate a project's activities, one unbounded
**Description.** `get_project_runtime_summary` uses
`activity_instance_repository.list_filtered(project_id, limit=10_000)`, but
`ProgressService.calculate_project_progress` uses
`activity_instance_repository.list()` (the **entire table, all projects**) then
filters in Python.

**Architectural risk.** Two definitions of "the activities of a project" with
different bounds. The progress path also scales with the whole database, not the
project.

**Operational consequence.** On a multi-project deployment, project progress
computation loads every activity in the system; and the `limit=10_000` cap vs.
unbounded list can yield different counts/results for the "same" question.

**Severity:** High.

**Stabilization direction.** Single project-scoped enumeration used everywhere;
remove the `.list()`-then-filter path.

### F15 — Status/threshold constant sets copy-pasted across analytics
**Description.** `_OPEN_BLOCKER`, `_PENDING_APPROVAL`, `_INACTIVE_WO`,
`_STALL_STEP(_STATUSES)` are redefined (with subtly different names) in
`operational_intelligence_service`, `decision_support_service`, and
`coordination_intelligence_service`.

**Architectural risk.** The operational definition of "open blocker" / "stalled
step" lives in 3 places. They agree today by luck/copy, not by design.

**Operational consequence.** A change to what counts as "open" in one module
produces inconsistent signals across the intelligence surfaces the user sees
side-by-side.

**Severity:** Medium.

**Stabilization direction.** One authoritative set of operational status groupings,
imported everywhere.

### F18 — Two unlinked identity systems for "who acted"
**Description.** Domain rows carry actor UUIDs (`created_by`, `submitted_by`,
`approved_by`, `reported_by`, `assigned_to`) with **no FK** to `platform_users`,
while the audit log records `username` + `role` strings. The two are never
correlated.

**Architectural risk.** "Who did this" has two representations that can disagree
and cannot be joined.

**Operational consequence.** Forensics/accountability is ambiguous: the row says
UUID X (or null), the audit says username Y — possibly different actors (see F1).

**Severity:** Medium.

**Stabilization direction.** Pick one authoritative attribution source and derive
the other; at minimum stop letting them diverge (see F1).

---

## 4. Derived truth ambiguity

### F3 — Same step shows two different progress numbers depending on endpoint
**Description.** `WorkflowStepRead.progress_percent` returns the **cached** column.
`runtime_router.list_workflow_steps` and `workflow-steps-batch` serve that cached
value with no recompute. But `get_workflow_step_runtime_view` returns
`current_progress` computed live, and `dashboard-summary` computes activity/project
progress live. So the list view and the detail/dashboard view can report different
progress for the same step.

**Architectural risk.** No single answer to "what is this step's progress." Two
truths shipped over the same API.

**Operational consequence.** Users see a step at, say, 0% in the list and 60% in
the detail panel — directly undermines trust in the numbers (compounded by F2,
where the cache is frozen).

**Severity:** High.

**Stabilization direction.** Choose one progress source for the API surface
(all-live, or all-cache-with-guaranteed-refresh) and use it consistently.

### F20 — Progress is unweighted while a weight field exists
**Description.** `WorkflowStep.planned_weight` exists, yet activity and project
roll-ups are **unweighted averages** (`ProgressService`). A 2-hour step and a
2-month step count equally.

**Architectural risk.** The data model implies weighting matters; the math says it
doesn't. Readers will assume weighting is applied.

**Operational consequence.** Project % can be wildly unrepresentative of actual
work done; a project dominated by many trivial completed steps reads as healthy.

**Severity:** Medium.

**Stabilization direction.** Either use `planned_weight` in roll-ups or remove the
implication that it's used (document "unweighted by design").

---

## 5. Authority ambiguity

### F1 — Domain attribution is client-controlled, not derived from the authenticated user
**Description.** `WorkflowStepApprovalCreate.approved_by` and
`DailyReportCreate.submitted_by` are optional client-supplied UUIDs. The runtime
router passes `payload.approved_by` / `payload.submitted_by` straight through to
the domain row, while the **audit** log records `current_user.username`. The
approver recorded in `approvals.approved_by` need not be the authenticated actor —
and can be any UUID, or null.

**Architectural risk.** The authority of a governance decision is asserted by the
request body, not by authentication. Two records of the same action (domain row vs
audit) can name different actors.

**Operational consequence.** Non-repudiation is broken: "User A approved step X"
in the domain can be fabricated by anyone with approver-role access; the audit and
the row disagree. For an approval/governance system this is the most dangerous
finding.

**Severity:** Critical.

**Stabilization direction.** Derive attribution from the authenticated principal,
not the payload; treat client-supplied actor fields as untrusted.

### F5 — Two roads to `APPROVED`, one of them unguarded
**Description.** A step reaches `APPROVED` via either `mark_inspection_passed`
(guards `status == INSPECTION_PENDING`) **or** `approve_workflow_step` (no source-
state guard; only blocks duplicate approval records). Planning create can also
mint a step already `APPROVED` (F4).

**Architectural risk.** "Approved" has no single precondition. The state means
different things depending on which door produced it.

**Operational consequence.** A step can be `APPROVED` without ever being inspected,
or while a blocker is open (F9), or directly at creation. The strongest governance
state is the least protected.

**Severity:** High.

**Stabilization direction.** Define one precondition set for `APPROVED` and route
both methods through it.

---

## 6. Lifecycle fragility

### F4 — Creation bypasses the lifecycle entirely
**Description.** `WorkflowStepCreate` accepts `status` (any legal string),
`progress_percent`, and `ready` directly from the client. Planning can create a
step that is born `APPROVED`, `progress_percent=100`, `ready=true` — no execution,
no work order, no inspection, no approval record.

**Architectural risk.** The lifecycle's starting state is whatever the client
declares. Every downstream invariant ("approved implies inspected", "progress
reflects work orders") is violable at birth.

**Operational consequence.** Fabricated completion is a single create call away,
and it won't match any work-order-derived progress (F2/F3).

**Severity:** High.

**Stabilization direction.** Constrain creation to legal initial states (e.g.
`PLANNED`, progress 0) and let services drive the rest.

### F17 — Concurrency safety is opt-in and silently defaults off
**Description.** Optimistic locking only engages when the caller passes
`expected_updated_at`. If omitted, `assert_unchanged` returns immediately and the
write is last-write-wins. The runtime schemas make these tokens optional.

**Architectural risk.** The integrity guarantee exists but is not enforced by
default; safety depends on every client remembering to send a token.

**Operational consequence.** Two supervisors editing the same step/work order can
silently clobber each other; the conflict detection that exists simply never fires.

**Severity:** High.

**Stabilization direction.** Make the token required for mutation endpoints (or
default-deny when absent) so the protection is the default, not the exception.

---

## 7. Analytics-semantic mismatch

### F9 — Blocker severity is operationally inert
**Description.** `Blocker` has rich `blocker_type` and `severity` (incl. `CRITICAL`)
and a real lifecycle, but **no domain rule reacts to it.** A `CRITICAL` open
blocker does not stop progress, does not block approval, does not change step
status. Only analytics interpret blockers (health deductions, coordination
signals).

**Architectural risk.** A concept that looks like a hard control is actually a
passive annotation. The enforcement people assume exists lives only in advisory
heuristics.

**Operational consequence.** A step can be approved and progressed to 100% while a
CRITICAL blocker is open. The "blocker" blocks nothing.

**Severity:** High.

**Stabilization direction.** Decide blocker's authority: if it's advisory, say so
explicitly; if it should gate execution/approval, route those operations through a
blocker check. Don't leave it ambiguous.

### F10 — Analytics infer approval states the write path never produces
**Description.** `operational_intelligence_service`, `decision_support_service`, and
`coordination_intelligence_service` all key off approvals in `PENDING` /
`UNDER_REVIEW` ("delayed pending approvals", "approval backlog", priority queue
ordering). But the only approval-creating path (`approve_workflow_step`) writes
records **directly as `APPROVED`**. Nothing in the system creates a `PENDING`
approval.

**Architectural risk.** A whole analytics surface is built on an operational
concept ("an approval awaiting decision") that the runtime doesn't generate. The
intelligence describes a workflow that isn't implemented.

**Operational consequence.** "Pending approval" metrics, queues, and supervisor
guidance are perpetually empty/misleading on real data — and look like a bug when
the queue is always empty despite work waiting.

**Severity:** High.

**Stabilization direction.** Reconcile the two: either the approval flow should
create `PENDING` records first, or the analytics should stop inferring a state the
domain never enters. Today they contradict each other.

### F16 — `COMPLETED` vs `APPROVED` step states overlap in meaning
**Description.** `WorkflowStep` has both `COMPLETED` and `APPROVED`. Governance only
ever sets `APPROVED`; `COMPLETED` is reachable only by set-only/creation. Progress
(work-order driven) is independent of both. So "done" is expressed three
unsynchronized ways: `status=COMPLETED`, `status=APPROVED`, and `progress=100`.

**Architectural risk.** No canonical definition of a finished step.

**Operational consequence.** Reports/filters disagree on what "complete" means;
each consumer picks a different field.

**Severity:** Medium.

**Stabilization direction.** Define the authoritative "done" predicate and the
relationship between `COMPLETED`, `APPROVED`, and `progress=100`.

---

## 8. Runtime semantic leakage

### F13 — `ValueError` is the catch-all; HTTP status is decided by string-sniffing
**Description.** Services raise plain `ValueError` for *both* "not found"
(`WorkOrder not found`) and "business rule violated" (`Duplicate assignment …`).
The router's `_http_from_runtime_error` then inspects the message:
`startswith("Duplicate")` → 409, otherwise → **404**. `ConcurrencyConflictError` is
the only typed exception.

**Architectural risk.** Control flow and HTTP semantics depend on error *message
text*. Rephrasing a message silently changes the API status code; a genuine
validation error (e.g. bad enum) is reported to clients as `404 Not Found`.

**Operational consequence.** Clients can't reliably distinguish "doesn't exist"
from "not allowed" from "bad input." Error handling on the frontend is built on a
fragile string contract.

**Severity:** High.

**Stabilization direction.** Introduce typed domain exceptions (not-found vs
conflict vs validation) at the service boundary; map by type, not by message
prefix. (Behavioral mapping can stay identical — this is about removing the string
dependency.)

### F19 — "Submit" daily report creates a `DRAFT`
**Description.** The endpoint/verb is `submit_daily_report`, but the report is
created with `status` defaulting to `DRAFT` (caller may pass another value). The
verb implies "submitted"; the default state says "draft."

**Architectural risk.** Operational terminology and persisted state disagree; the
action name doesn't drive the lifecycle.

**Operational consequence.** A "submitted" report sits in `DRAFT`; downstream
review states (`SUBMITTED/REVIEWED/ACCEPTED`) are never driven by the submit verb,
so the report-review lifecycle is inert (like F6/F10).

**Severity:** Medium.

**Stabilization direction.** Align verb and resulting state, or document that
"submit" is "create in caller-chosen state" and define who advances the review
lifecycle.

---

## Cross-cutting themes

Three root patterns generate most of the findings:

1. **The DB CHECK is the only enforcement.** Most "lifecycle" is value-set
   validation, not transition validation (F4, F5, F6, F8, F16, F19). The rich
   status vocabularies imply workflows that no code drives.

2. **Derived truth has no custodian.** Progress is the clearest victim: a hinge
   status (`WorkOrder=COMPLETED`) drives a formula whose cache is never refreshed,
   exposed inconsistently next to live recomputation (F2, F3, F12, F20).

3. **Authority is asserted, not derived.** Attribution and approval trust the
   request body; concurrency and access boundaries default to permissive
   (F1, F7, F17). For a system whose core value is *governance of construction
   execution*, this is the most important class to stabilize.

## Suggested triage order (stabilization, not redesign)

1. **F1** (client-controlled approver) and **F2/F3** (progress truth) — these
   produce wrong operational/authority truth today.
2. **F4, F5, F17** — lifecycle/concurrency can be tightened at existing chokepoints
   without API change.
3. **F9, F10, F16, F19** — reconcile analytics-implied concepts with what the
   runtime actually produces.
4. **F11, F12, F14, F15, F18** — consolidate duplicated semantics into single
   sources.
5. **F6, F8, F13, F20** — document or centralize the convention-based behavior so
   it stops masquerading as enforced.

All recommendations above are **directions**, deliberately implementable within the
current architecture, models, and API contracts. No event sourcing, no new
entities, no new systems.

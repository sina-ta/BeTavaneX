# COSC — Immutable Operational Event Ledger (Foundation)

> Lightweight, append-only operational **lineage** that coexists with the existing
> state-oriented architecture. This is **not** event sourcing: current state stays
> owned by the domain tables. The ledger records *that an operation happened*, by
> *whom*, *when*, and *about what* — it never becomes the source of truth for
> current state.
>
> Scope of this foundation: one table, one taxonomy, one append-only repository,
> one recording service, and integration for exactly five event types. No Kafka,
> no CQRS, no repository/service redesign, no API contract changes.

## 1. What was added

| Artifact | Path |
|---|---|
| ORM model | `backend/phase1/models/operational_event.py` |
| Taxonomy | `backend/phase1/events/taxonomy.py` |
| Append-only repository | `backend/phase1/repositories/operational_event_repository.py` |
| Recording service | `backend/phase1/events/event_recording_service.py` |
| DI providers | `backend/phase1/dependencies/events.py` |
| Migration | `backend/alembic/versions/20260603_0004_operational_events.py` |
| Model registration | `backend/phase1/models/__init__.py` |
| Integration (3 events) | `backend/phase1/routers/runtime_router.py` |
| Integration (2 events) | `backend/phase1/services/workflow_governance_service.py` (+ DI in `dependencies/services.py`) |

Nothing existing was removed or rewritten. The governance service gained one
**optional** constructor parameter (`event_recorder=None`), so all prior call
sites and tests keep working unchanged.

## 2. Event model

Table `operational_events` (new head revision `20260603_0004`).

| Field | Column | Type | Notes |
|---|---|---|---|
| `event_id` | `event_id` | UUID PK | server `gen_random_uuid()` |
| `event_type` | `event_type` | varchar(100) | CHECK-constrained to the 5 supported types |
| `aggregate_type` | `aggregate_type` | varchar(100) | reuses domain vocabulary (`work_order`, `daily_report`, `workflow_step`, `blocker`) |
| `aggregate_id` | `aggregate_id` | UUID | the domain row the event is about |
| `actor` | `actor` | varchar(150) | username (or `system`); never null |
| `timestamp` | `occurred_at` | timestamptz | event time, set by the recorder in UTC |
| `causality_reference` | `causality_reference` | UUID, nullable | soft link to a prior `event_id` (no FK) |
| `payload` | `payload` | JSONB | operational facts of the event |
| `metadata` | `metadata` | JSONB | context (role, project_id, source) |
| — | `created_at` | timestamptz | server-stamped ledger-write time |

Two timestamps on purpose:

- `occurred_at` — when the operation happened (application/UTC, the lineage time).
- `created_at` — when the row was appended (DB default), the immutable write
  receipt. They are normally equal but `created_at` is the tamper-evident anchor.

> Note: the Python attribute for the `metadata` column is `event_metadata`,
> because `metadata` is reserved by SQLAlchemy's declarative base. The DB column is
> still named `metadata` as required.

Indexes: `(aggregate_type, aggregate_id)`, `event_type`, `occurred_at`, `actor`,
`causality_reference` — covering the natural lineage queries ("history of this
aggregate", "all events of a type", "what did this actor do", "what did this
event cause").

## 3. Event taxonomy

Defined in `events/taxonomy.py`. Intentionally narrow.

**Supported event types (the only ones implemented):**

| event_type | aggregate_type | aggregate_id | recorded at |
|---|---|---|---|
| `work_order_assigned` | `work_order` | work order id | runtime router (`/runtime/work-orders/{id}/assign`) |
| `daily_report_submitted` | `daily_report` | daily report id | runtime router (`/runtime/daily-reports`) |
| `approval_completed` | `workflow_step` | workflow step id | runtime router (`/runtime/workflow-steps/{id}/approve`) |
| `blocker_registered` | `blocker` | blocker id | `WorkflowGovernanceService.add_blocker` |
| `blocker_resolved` | `blocker` | blocker id | `WorkflowGovernanceService.resolve_blocker` |

`approval_completed` anchors on the **workflow step** (the durable operational
subject the approval governs), not the approval row — so a step's full governance
lineage is queryable by one `aggregate_id`.

Aggregate types reuse existing domain terms; **no new operational concepts** were
invented. The CHECK constraint, the model, and the recorder all derive their
allowed set from this one module.

## 4. Event lifecycle

An event has exactly one transition: **non-existent → appended**. That is the
entire lifecycle.

```
operation succeeds (assign / submit / approve / add-blocker / resolve-blocker)
        │
        ▼
EventRecordingService.record_*  ──builds OperationalEvent (typed, UTC, actor)──┐
        │                                                                      │
        ▼                                                                      │
OperationalEventRepository.append  ──session.add + flush──▶ row staged         │
        │                                                                      │
        ▼                                                                      │
request transaction commits (get_db)  ◀───────────────────────────────────────┘
        │
        ▼
event is permanent: no update path, no delete path
```

There is no draft, no pending, no correction state. An event is a fact about the
past.

## 5. Append-only guarantees

Immutability is enforced at multiple layers, not by convention:

1. **No update/delete API.** `OperationalEventRepository` exposes `append` +
   read methods only. It does **not** extend `BaseRepository`, so it inherits no
   `update`/`delete`.
2. **Hard guards.** The repository defines `update()` and `delete()` that raise
   `EventLedgerImmutabilityError`. Any accidental call fails loudly.
3. **Existing delete policy.** `integrity/delete_policy.assert_delete_allowed`
   only permits `WorkOrderWorkflowStep` and `BOQMapping`; `OperationalEvent` is not
   on the allowlist, so even a generic delete path is refused.
4. **No mutators in the recorder/service.** The recording service only constructs
   and appends; it never loads-and-edits an event.
5. **Single write path.** `append` is the only way a row enters the table in
   application code.

Database-level note: PostgreSQL still permits raw `UPDATE/DELETE` by a superuser;
this foundation makes the **application** append-only. A future hardening step
could add a DB trigger or a restricted role — see §8.

## 6. Causality semantics

`causality_reference` is an **optional soft pointer** to a prior `event_id`,
establishing "this event happened because of that one."

- It is **nullable** and carries **no foreign key** — deliberately. A FK would
  couple the ledger to itself and complicate the append-only guarantee; lineage
  links must never block or cascade.
- In this foundation it is populated where a natural prior event exists and is
  known to the caller; otherwise left null. None of the five types *require* it.
- Semantics: a non-null `causality_reference` means "trace back to event X for the
  cause." It is a hint for lineage reconstruction, never an integrity constraint.
- Aggregate-level causality is always available regardless of this field: events
  sharing an `aggregate_id` are time-ordered by `occurred_at`, giving the full
  history of that work order / step / blocker without explicit links.

## 7. Integration boundaries

The ledger is wired at the points where operations actually occur and where actor
context exists — mirroring the existing `log_operational_action` audit calls.

- **Router-level (3 events).** `assign_work_order`, `submit_daily_report`,
  `approve_workflow_step` each take an injected `EventRecordingService` and record
  **after** the use-case call succeeds. Actor = the authenticated `current_user`
  (not client-supplied). This sits beside the existing audit logging; both run in
  the same request transaction.
- **Service-level (2 events).** Blockers have no HTTP endpoint today, so
  `add_blocker` / `resolve_blocker` record through the **optional** recorder
  injected into `WorkflowGovernanceService`. If the recorder is absent (unit
  tests), recording is a silent no-op.

### Transactional boundary

The event repo is built from the same request-scoped `Session` as every other
repository (`get_db` is cached per request). Therefore:

- An event is committed **in the same transaction** as the operation it records.
- If the operation rolls back, the event rolls back too → no orphan lineage.
- If the event append fails, the operation fails too → no silent lineage gaps.

This "same-transaction" choice is intentional: lineage must be consistent with
state. It is the correct trade-off for a foundational ledger and adds one trivial
INSERT per recorded operation.

### What the integration does NOT touch

- No API request/response schema changed (the recorder reads already-available
  data: path params, payload, the created entity, `current_user`).
- No business logic moved. Recording is additive and side-effect-only.
- No new endpoints, no new roles, no analytics changes.

## 8. Relationship to existing observation surfaces

BetavanX already had two **observation** logs (see `event-taxonomy.md`):
`operational_audit.jsonl` and `operational_usage.jsonl`. Those remain unchanged.
The new ledger differs in three ways:

| | Audit/usage JSONL | Operational event ledger |
|---|---|---|
| Store | files on disk | relational table (transactional) |
| Consistency | best-effort, outside the txn | same transaction as the operation |
| Purpose | adoption/diagnostics | durable operational lineage/causality |
| Authority | observational, discardable | durable record (still not current-state truth) |

The ledger does not replace the audit log; it is the transactional, query-friendly
lineage spine the JSONL logs were never meant to be.

## 9. Future expansion considerations

Deliberately out of scope now; recorded so the foundation can grow without rework:

1. **More event types.** Add a constant + register in `SUPPORTED_EVENT_TYPES`
   (and `EVENT_AGGREGATE_TYPE`), then add the CHECK value in a new migration. The
   model, repository, and recorder need no structural change.
2. **Read API.** A `/runtime/.../lineage` endpoint over
   `list_for_aggregate` / `list_by_type` would expose history; the repository read
   methods already exist.
3. **DB-level immutability.** A trigger blocking `UPDATE`/`DELETE`, or a
   write-restricted DB role, to extend append-only from the app to the database.
4. **Richer causality.** Populate `causality_reference` more systematically (e.g.
   `blocker_resolved` → the `blocker_registered` event) once event ids are threaded
   through services.
5. **Projection/replay (only if ever needed).** Because events are consistent with
   state, derived read-models could be built later — but this remains explicitly
   **not** event sourcing; state stays authoritative in the domain tables.
6. **Hash chaining.** For tamper-evidence, a future field could chain each event to
   the previous one's hash. Not implemented; noted only as a direction.

## 10. Operational guarantees summary

- Events are **immutable, append-only, timestamped, and actor-attributed.**
- No update path, no delete path (enforced at repository + policy layers).
- Recording is **transactional** with the operation it records.
- Five event types only; aggregates reuse existing domain vocabulary.
- Coexists with — and does not alter — current state, APIs, services, or analytics.

# Runtime Hardening P1 — Authoritative Dependency Edge Foundation

> First implementation-oriented stabilization phase after COSC semantic consolidation.
> Establishes **explicit dependency existence** — not propagation, scheduling, or graph
> runtime.

## Objective

Close the critical gap identified across COSC audits: the runtime had **no
authoritative operational dependency edge model**. Sequencing existed only through
convention, workflow adjacency, lifecycle implication, or analytics interpretation.

P1 introduces a minimal substrate that:
- coexists with the current state-oriented runtime,
- records authoritative dependency semantics at creation,
- enforces integrity constraints,
- emits immutable lineage events,
- exposes read-only inspection/trace APIs.

## Implemented substrate

### 1. Data model — `operational_dependency_edges`

| Field | Purpose |
|---|---|
| `id` | Edge identity (lineage aggregate) |
| `project_id` | Same-project scope (integrity anchor) |
| `source_entity_type` / `source_entity_id` | Dependency source |
| `target_entity_type` / `target_entity_id` | Dependency target |
| `dependency_type` | Authoritative type (taxonomy-grounded) |
| `authority_level` | Stamped at creation (`hard` / `soft` / …) |
| `blocking_semantics` | Recorded blocking meaning (not executed in P1) |
| `propagation_semantics` | Recorded propagation meaning (not executed in P1) |
| `lifecycle_status` | `active` / `deactivated` |
| `created_by` / `created_at` | Server-side attribution |
| `deactivated_at` / `deactivated_by` / `deactivation_reason` | Soft removal |
| `metadata` | Optional JSONB context |

**Migration:** `20260603_0005_dependency_edges.py` (Alembic head).

### 2. Taxonomy — `backend/phase1/dependency_edges/taxonomy.py`

Grounded in `docs/cosc/dependency-semantics-stabilization.md`. Only types requiring
*explicit* edges:

| Type | Authority | Blocking (recorded) | Propagation (recorded) | Allowed endpoints |
|---|---|---|---|---|
| `execution_dependency` | hard | none | pull_bottom_up | step↔step, activity↔activity |
| `readiness_dependency` | soft | none | none | step↔step, step↔activity |
| `resource_dependency` | soft | none | none | step→step |
| `spatial_dependency` | soft | none | none | activity→activity |
| `governance_dependency` | hard | state_transition | step_status_only | step→step |

**Intentionally excluded** (already structural or observational):
`containment_dependency` (FKs), `coordination_dependency` link (junction table),
`coordination_dependency` handoff (analytics), `informational_dependency`.

Semantics are **stamped automatically** from taxonomy at creation — callers cannot
supply arbitrary authority/blocking/propagation values.

### 3. Integrity guarantees (`dependency_edge_policy.py`)

Enforced at creation/deactivation (no propagation engine):

- **No self-links** (`source_entity_id != target_entity_id`, DB + service).
- **No cross-project edges** — both endpoints resolved to `project_id` and must
  match the edge's `project_id` (closes invalid pattern #1 class for explicit edges).
- **Entity existence** — source/target rows must exist.
- **Dependency type ↔ entity pair** — type must allow the source/target entity types.
- **No duplicate active edges** — partial unique index on active identity tuple.
- **No direct reverse active edge** for sequencing types (execution, readiness,
  governance, spatial).

Edges are **deactivated, not deleted** — history preserved; lineage remains queryable.
Hard delete is blocked by existing `delete_policy` (not in allowed junction set).

### 4. Event lineage integration

Two new ledger event types (append-only, same transaction as edge mutation):

- `dependency_edge_created`
- `dependency_edge_deactivated`

Aggregate type: `dependency_edge`. Payload includes full edge identity and stamped
semantics. Reuses `EventRecordingService` — no ledger redesign.

Operational audit JSONL also records `create_dependency_edge` /
`deactivate_dependency_edge` (planning category).

### 5. Service & API (`DependencyEdgeService`, `dependency_router`)

**Mutations** (admin/supervisor, planning authority):
- `POST /runtime/projects/{project_id}/dependency-edges`
- `POST /runtime/projects/{project_id}/dependency-edges/{edge_id}/deactivate`

**Read-only visibility** (all runtime readers):
- `GET /runtime/projects/{project_id}/dependency-edges` — list/filter
- `GET /runtime/projects/{project_id}/dependency-edges/{edge_id}` — inspect
- `GET /runtime/projects/{project_id}/dependency-edges/trace` — incoming/outgoing
- `GET /runtime/projects/{project_id}/dependency-edges/{edge_id}/lineage` — ledger events

No orchestration UI changes. No automatic behavior triggered by reads.

## Intentionally deferred complexity

| Capability | Status |
|---|---|
| Automatic propagation | **Not implemented** — semantics recorded only |
| Critical path / float | **Not implemented** — no traversal engine |
| Scheduling intelligence | **Not implemented** |
| Graph DB / traversal engine | **Not implemented** |
| Dependency optimization | **Not implemented** |
| Realtime sync | **Not implemented** |
| Simulation behavior | **Not implemented** |
| Multi-hop cycle detection | **Not implemented** — only direct reverse guard |
| Blocking enforcement at runtime | **Not implemented** — blocking_semantics recorded |
| Readiness derivation from edges | **Not implemented** — edges are inputs, not computed readiness |
| Backfill of implicit FK/junction deps | **Not implemented** — explicit edges only |

## Known limitations

1. **Existence only.** Creating an edge declares a dependency; nothing in the runtime
   yet *acts* on it (no gating, no propagation, no readiness computation).
2. **Partial cycle protection.** Direct A↔B reverse pairs are blocked; longer cycles
   (A→B→C→A) are not detected in P1.
3. **`work_order` entity type** is allowed at the schema level but no dependency type
   currently permits work-order endpoints — reserved for future explicit coordination
   edges without schema migration.
4. **Implicit dependencies remain implicit.** FK containment, WO↔step junction links,
   and analytics handoffs are not mirrored into this table.
5. **Deactivation is the only correction path.** Reactivation requires creating a new
   edge after deactivation (partial unique index allows this).
6. **Governance/execution runtime** still does not consult edges before
   approval/execution (semantic gap A11/A15 remains at behavior layer).

## Future propagation boundaries

When propagation is eventually implemented, the stabilization docs require:

1. **Respect stamped semantics** — `blocking_semantics` and `propagation_semantics`
   on each edge are the contract; P1 already stores them authoritatively.
2. **Same-project invariant** — propagation must never cross `project_id`.
3. **Lineage-first** — any future propagation side-effect should emit ledger events;
   never silent mutation.
4. **Service ownership** — propagation logic belongs in existing owners
   (`ProgressService`, `WorkflowGovernanceService`), not a new orchestration layer.
5. **No auto-gating from analytics** — edges may inform readiness/governance; advisory
   layers still cannot mutate state (`runtime-authority-boundaries.md`).

## Files added/changed

**New:**
- `backend/phase1/dependency_edges/taxonomy.py`
- `backend/phase1/models/operational_dependency_edge.py`
- `backend/phase1/repositories/operational_dependency_edge_repository.py`
- `backend/phase1/integrity/dependency_edge_policy.py`
- `backend/phase1/services/dependency_edge_service.py`
- `backend/phase1/schemas/dependency_edge_schema.py`
- `backend/phase1/routers/dependency_router.py`
- `backend/alembic/versions/20260603_0005_dependency_edges.py`

**Updated:**
- Event taxonomy + `EventRecordingService` (2 event types)
- `operational_events` CHECK constraint (migration)
- DI providers, `app.py` router mount, model registry
- Alembic head expectations in validation scripts (`20260603_0005`)

## Verification

```bash
python -c "from backend.phase1.app import create_app; create_app(); print('app OK')"
alembic -c backend/alembic.ini upgrade head
```

After migration: table `operational_dependency_edges` present; `alembic_version =
20260603_0005`.

## Bottom line

P1 answers the question **"does this dependency exist, with what authoritative
meaning?"** — not **"what does the dependency do?"** That separation is deliberate:
semantic stabilization defined the meaning; this phase makes existence explicit and
integrity-safe; future hardening phases may add enforcement and propagation **within
existing service boundaries**, without a graph database or orchestration redesign.

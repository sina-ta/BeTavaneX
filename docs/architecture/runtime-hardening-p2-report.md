# Runtime Hardening P2 — Derived Readiness Ownership

> Authoritative readiness **derivation** only — not scheduling, propagation, or
> orchestration. Grounded in COSC semantic stabilization and P1 dependency edges.

## Objective

Replace direct readiness authority with a **derived operational interpretation**
owned by `ReadinessDerivationService`. Readiness answers: *can execution safely and
operationally proceed?* — as an explainable, attributable verdict.

## Implemented

### 1. Derived readiness evaluation layer

| Component | Path |
| --- | --- |
| Pure evaluation | `backend/phase1/readiness/derivation.py` |
| Service owner | `backend/phase1/services/readiness_derivation_service.py` |

**Evidence inputs (no scoring engine):**

| Source | Effect |
| --- | --- |
| `workflow_status` | Executable band (PLANNED, IN_PROGRESS, …) vs terminal states |
| `blocker` | Open blockers → not ready + contradiction if stored `ready=true` |
| `dependency_edge` | Incoming execution/readiness/governance/resource edges (P1 substrate) |
| `stored_ready_column` | Surfaces `stored_vs_derived` contradictions |

**Output:** `derived_ready`, `contributing_conditions`, `blocking_conditions`,
`contradictions`, `evidence_sources`, `interpretation_summary`.

The `workflow_steps.ready` column is a **synchronized cache** written only by the
deriver after evaluation — not a free assertion.

### 2. Readiness authority boundaries

| Guard | Behavior |
| --- | --- |
| `reject_direct_ready_mutation()` | Rejects `ready=True` on planning create (422) |
| Planning create | Always persists `ready=False`, then `initialize_workflow_step()` |
| No update path | `WorkflowStepUpdate.ready` remains unused in routers |

Direct `ready=true` from clients is **authoritatively illegal**.

### 3. Readiness lineage integration

New operational event types (Alembic `20260603_0006`):

| Event | When recorded |
| --- | --- |
| `readiness_evaluated` | Derivation refresh without ready flip |
| `readiness_blocked` | `prior_ready=true` → `derived_ready=false` |
| `readiness_recovered` | `prior_ready=false` → `derived_ready=true` |

Aggregate: `workflow_step`. Payload includes full interpretation + `trigger`.
`causality_reference` links to blocker/dependency ledger events when applicable.

**Chokepoints wired:**

- Workflow step creation (planning)
- Blocker register / resolve (`WorkflowGovernanceService`)
- Dependency edge create / deactivate (`DependencyEdgeService`, workflow_step targets)

### 4. Read-only readiness inspection

| Endpoint | Purpose |
| --- | --- |
| `GET /runtime/projects/{project_id}/workflow-steps/{workflow_step_id}/readiness` | Interpretation + conditions + contradictions |
| `GET .../readiness/lineage` | Readiness-specific ledger events |

Runtime readers only. No orchestration UI changes.

## Authority guarantees

1. **Single deriver** — only `ReadinessDerivationService` may set `workflow_steps.ready`.
2. **Explainable** — every not-ready verdict cites blocking conditions with evidence source.
3. **Contradiction visibility** — stored vs derived and ready-with-blockers are surfaced, not hidden.
4. **Attributable** — lineage events carry actor, trigger, causality_reference, project metadata.
5. **Advisory** — derived readiness does not block assignments, approvals, or execution APIs.

## Intentionally deferred complexity

| Capability | Status |
| --- | --- |
| Scheduling / propagation engines | **Not implemented** |
| Multi-hop dependency traversal | **Not implemented** — single-hop incoming edges only |
| Automatic execution gating | **Not implemented** |
| AI / predictive readiness | **Not implemented** |
| Resource availability integration | **Edge-declared only** — no external resource system |
| Activity-level readiness refresh | **Not implemented** — workflow_step targets only |
| Governance consult hook | **Not implemented** — approvals do not yet consult readiness |
| Backfill of legacy `ready=true` rows | **Not implemented** — contradictions visible on inspect |

## Remaining semantic gaps

1. **Soft violations allowed** — execution may proceed when `derived_ready=false` (philosophy axiom: reality may precede readiness); contradictions are surfaced, not enforced.
2. **Implicit dependencies** — FK containment and WO↔step junction links are not inputs yet (P1 scope).
3. **Governance precedence** — acceptance paths do not consult readiness before approval (A15 gap remains at behavior layer).
4. **Long cycles** — only direct incoming edges evaluated; no graph closure.

## Future propagation boundaries

When propagation is considered (post-P2):

- Readiness remains **derived**, never client-writable.
- Propagation may **re-invoke** the deriver on affected steps; it must not bypass lineage.
- Hard dependencies (`execution_dependency`, `governance_dependency`) gate semantics are recorded on edges; enforcement belongs in existing owners (`WorkflowGovernanceService`, `WorkflowExecutionService`), not a new orchestration layer.
- Analytics and intelligence layers remain read-only with respect to readiness.

## Files

**New:**

- `backend/phase1/readiness/authority.py`
- `backend/phase1/readiness/derivation.py`
- `backend/phase1/services/readiness_derivation_service.py`
- `backend/phase1/schemas/readiness_schema.py`
- `backend/phase1/routers/readiness_router.py`
- `backend/alembic/versions/20260603_0006_readiness_lineage_events.py`
- `backend/scripts/runtime_hardening_p2_verification.py`

**Changed:**

- `backend/phase1/events/taxonomy.py`
- `backend/phase1/events/event_recording_service.py`
- `backend/phase1/routers/planning_router.py`
- `backend/phase1/services/workflow_governance_service.py`
- `backend/phase1/services/dependency_edge_service.py`
- `backend/phase1/dependencies/services.py`
- `backend/phase1/application/planning_use_cases.py`
- `backend/phase1/app.py`

## Verification

```bash
PYTHONPATH=. python backend/scripts/runtime_hardening_p2_verification.py
```

Degraded pass (exit 0) when PostgreSQL unavailable — unit derivation + API shape checks still run.

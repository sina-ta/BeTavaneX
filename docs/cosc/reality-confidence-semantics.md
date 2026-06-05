# COSC — Reality Confidence Semantics

> How **operational confidence, uncertainty, evidence strength, and observation
> trustworthiness** behave semantically in BetavanX. This defines *how much a claim
> about reality can be trusted* — separate from whether that claim is the
> authoritative record.
>
> **Semantic definition only.** No scoring engine, no probabilistic model, no ML, no
> AI arbitration, no autonomous trust system, no runtime/governance redesign.
> Confidence here is **qualitative and interpretive** — never a computed number,
> never stored authoritative state. Where the runtime already does something
> confidence-adjacent, it is cited; where it fakes confidence, it is called out.

## Grounding

Built on: `operational-philosophy.md` (esp. #2 "reports are observations" and #10
"analytics without semantics is heuristic theater"), `truth-reconciliation-semantics.md`
(§5 confidence & evidence), `lifecycle-semantics-stabilization.md`,
`dependency-semantics-stabilization.md`, `operational-assumption-registry.md`,
`execution-physics.md`, `event-taxonomy.md`.

The anchor axiom: **a report is not automatically truth** (philosophy #2). Its
reliability depends on actor authority, supporting evidence, execution consistency,
contradiction presence, and governance validation. This document formalizes that
sentence — and nothing more ambitious.

---

## 1. Operational Confidence Model

### 1.1 What confidence means operationally
Confidence is the **qualitative trustworthiness of a claim as a representation of
execution reality.** It is a property of *the observation/derived value*, not of
reality itself. "High confidence" means *well-corroborated by authority, evidence, and
lineage*; "low confidence" means *weakly supported, stale, or contradicted.*

### 1.2 What confidence is NOT
- **Not truth.** Truth = the authoritative DB record (`truth-contracts.md`). Confidence
  = how much we trust that record reflects reality. They are **orthogonal**.
- **Not a probability or score.** No number is computed or stored. The runtime's
  `confidence: high/medium/low` strings in `decision_support_service` are *deterministic
  threshold labels*, not measured confidence — "confidence theater" (A10) unless tied to
  real evidence.
- **Not governance approval.** Approval is an acceptance authority act; confidence is an
  interpretive property (see §5).
- **Not certainty.** High confidence can still be wrong (Q2).
- **Not authoritative state.** Confidence must never become a stored field that other
  layers treat as truth, or it becomes exactly the theater philosophy #10 warns against.

### 1.3 Confidence vs truth
Operational truth is authoritative regardless of confidence. A stale
`progress_percent` cache is *truth in the DB* but *low-confidence as reality* (A3). A
work order marked `COMPLETED` is execution truth even if no daily report corroborates
it — just at lower confidence.

### 1.4 Confidence vs governance
Governance produces **acceptance**, not confidence. Approval *can raise* confidence
when it adds genuine corroboration (an authority validated the claim against evidence);
it *only acknowledges* when it rubber-stamps without consulting evidence (current
bypassable approval — A15). Approval never *creates* reality (axiom #3), so it can never
make a false claim true — only accepted.

### 1.5 Confidence vs evidence
Evidence is the **basis**; confidence is the **interpretation** of evidence strength,
corroboration, freshness, and contradiction. No evidence → confidence rests on bare
authority alone (weak). Conflicting evidence → confidence drops, contradiction is
surfaced.

### 1.6 The qualitative confidence vocabulary (not a scale to compute)
Used descriptively only — never as numbers, never stored:

| Descriptor | Means | Typical basis |
|---|---|---|
| **Grounded** | corroborated by evidence + lineage + (optionally) governance | report + completion + approval agree |
| **Asserted** | a single authoritative claim, no corroboration | one supervisor report; a set status |
| **Derived** | computed from rows; only as fresh as last computation | progress recomputation |
| **Inferred** | analytics interpretation over heuristics | a derived signal |
| **Stale** | once-trustworthy, now aged past freshness | `updated_at` past `OPS_STALL_DAYS` |
| **Unknown** | source unavailable / no basis | `data_available: false` |

---

## 2. Observation Trustworthiness Factors

The factors that raise or lower confidence — **defined qualitatively, never summed
into a score** (philosophy #2's list, mapped to real fields):

| Factor | Raises confidence when… | Lowers confidence when… | Runtime signal |
|---|---|---|---|
| **Actor authority** | a supervisor/admin observes/validates | a low-authority actor asserts beyond their role | `role` on audit/report |
| **Evidence presence** | a daily report / attachment / lineage backs the claim | the claim is bare (status set, no evidence) | `daily_reports`, ledger |
| **Execution consistency** | the claim matches progress/commitments | status, progress, and commitments disagree | three-"done" (A17) |
| **Contradiction presence** | no conflicting signal | a conflicting layer/signal exists | reconciliation §2 |
| **Timing freshness** | recently updated | `updated_at` aged past stall thresholds | `OPS_STALL_DAYS` |
| **Lineage consistency** | event ledger corroborates the sequence | no/contradictory lineage | event ledger |
| **Governance validation** | an authority validated against evidence | unvalidated, or rubber-stamped | `Approval`, inspection |

Authoritative rule: **these factors are read together by a human/interpretation layer**,
qualitatively. The platform must not collapse them into a single computed trust number
— that would manufacture false precision (A10).

---

## 3. Evidence Semantics

### 3.1 Evidence types
- **Structural evidence** — DB invariants (existence, uniqueness): strongest, cannot be
  contradicted.
- **Observational evidence** — daily reports: direct field observation; reliability
  depends on actor authority (philosophy #2).
- **Derived evidence** — progress computed from commitments: only as fresh as its
  recomputation (cache caveat, A3).
- **Lineage evidence** — the event ledger: immutable record *that* an action occurred,
  by whom, when.
- **Governance evidence** — approvals/inspections: corroboration via authority act.

### 3.2 Evidence strength (qualitative ordering, from reconciliation §5.2)
```
structural  >  corroborated + governance-validated  >  corroborated observation
   >  single authoritative observation  >  single field observation
      >  bare declaration  >  analytic inference
```

### 3.3 Supporting vs conflicting evidence
- **Supporting** evidence (multiple sources agree) → grounded confidence.
- **Conflicting** evidence → confidence drops; **surface both, collapse neither**
  (reconciliation §5.4). The system never silently picks a winner.

### 3.4 Missing evidence
**Absence of evidence is not falsity.** Missing evidence *lowers confidence* but does
**not** invalidate execution truth (axiom #3, Q5). A `COMPLETED` work order with no
report is still execution truth — at reduced confidence pending corroboration.

### 3.5 Observational vs derived evidence
- Observational evidence ages by **freshness** (when was it observed).
- Derived evidence ages by **computation** (when was it last recomputed) — a derived
  value can be *structurally* approximate even when fresh (unweighted progress, binary
  work-order contribution — A1/A2). Derived evidence therefore carries *two*
  uncertainties: staleness **and** derivation method.

---

## 4. Uncertainty Taxonomy

Uncertainty is **named, never measured**. The kinds that genuinely exist in this
runtime:

| Uncertainty | What it is | Real source |
|---|---|---|
| **Staleness** | once-true value now aged | stale `updated_at`; stale progress cache (A3) |
| **Attribution** | "who *claimed* to act" — soft, unverified | soft UUID `approved_by`/`reported_by` (A18) |
| **Interpretation** | heuristic may be a false positive | analytics `false_positive_notes`, thresholds |
| **Completeness** | required observation absent | no daily report; no inspection before approval |
| **Derivation** | the formula is structurally approximate | unweighted roll-up, binary WO (A1/A2) |
| **Existence** | a referenced state never occurs | analytics inferring `PENDING` approvals (invalid pattern #8) |
| **Ambiguity** | the concept itself is undefined | three definitions of "done" (A17); meaningless `ready` (A4) |

### 4.1 Unresolved uncertainty
May persist (philosophy #8) **if surfaced**. Forbidden: hidden uncertainty presented as
certainty.

### 4.2 Stale observations
A stale observation is **not false** — it is *low-confidence-by-age*. It remains truth
until superseded; consumers should re-derive/re-observe before trusting.

### 4.3 Incomplete observations
A partial observation (e.g. a `DRAFT` report, a step with no inspection) carries
**completeness uncertainty**; it informs but does not ground confidence.

### 4.4 Ambiguous operational states
Where the concept is undefined (which "done"? what does `ready` mean?), confidence is
**unassignable** — the right response is to *resolve the ambiguity* (A17/A4), not to
fabricate a confidence label.

---

## 5. Confidence vs Governance

| Situation | Governance effect | Confidence effect |
|---|---|---|
| Approval **after** inspection + report, by authority | accepts | **raises** (corroboration added) |
| Approval with no inspection / no report (bypass) | accepts | **none** — only acknowledgement (A15) |
| Approval over open `CRITICAL` blocker | accepts (currently) | **lowers** — contradiction; should be forbidden (A5) |
| Rejection of a well-evidenced observation | changes acceptance | high-confidence contradiction → escalate |
| Recomputation of progress | n/a (not governance) | refreshes derived confidence |

Authoritative rules:
1. **Governance increases confidence only by adding corroboration** — an authority
   validating a claim *against evidence*.
2. **Governance that consults nothing only acknowledges** — it adds acceptance, not
   confidence.
3. **Governance cannot resolve uncertainty about physical reality** (axiom #3):
   approving a stale measurement does not make it accurate; it makes it *accepted*.
4. **Confidence vs approval distinction:** approval is a binary acceptance act;
   confidence is the qualitative trust in the underlying reality. A step can be
   `APPROVED` (high acceptance) yet low-confidence (no evidence, stale progress).

---

## 6. Contradiction Confidence Rules

Confidence determines how seriously a contradiction is taken (extends reconciliation
§2, escalation §6):

- **High-confidence contradiction** — both conflicting claims are well-evidenced (e.g. a
  corroborated field report vs a governance rejection; `COMPLETED` work order vs a
  failed inspection). → **Escalate**; requires human/governance reconciliation; must not
  persist silently.
- **Low-confidence contradiction** — at least one claim is weakly evidenced (e.g.
  analytics inferring a `PENDING` approval the write path never creates). → Likely false
  positive; low priority; correct the inference, don't escalate.
- **Conflicting evidence** — surface both; lower the effective confidence of the claim;
  never auto-resolve.
- **Governance disagreement** — governance contradicting well-evidenced execution is a
  **high-confidence contradiction** worth escalating (and a signal to check whether
  governance consulted the evidence).
- **Observation divergence** — two reports disagree; confidence of each follows actor
  authority + corroboration; the platform presents both, ranked qualitatively, and lets
  an authority decide.

---

## 7. Event Lineage Expectations

**No implementation here** — how confidence-affecting events *should* appear in
lineage:

1. **Evidence events are confidence inputs.** `daily_report_submitted`,
   `approval_completed`, inspection pass/fail, `blocker_registered/resolved` each *raise
   or lower* the confidence of the related state — lineage is the substrate from which
   confidence is later read.
2. **Corroboration is visible in lineage**, not stored as a score. Multiple
   independent events about the same aggregate = grounded confidence, readable from the
   ledger.
3. **Contradiction and its reconciliation appear side by side** (reconciliation §8):
   a `causality_reference` thread shows the conflicting event and the act that
   reconciled it — so confidence *history* is reconstructable.
4. **Freshness is a lineage property** (`occurred_at`): staleness uncertainty is read
   from event timing, not invented.
5. **Confidence itself is never a stored event.** Lineage records *facts and acts*;
   confidence is *derived from them by interpretation*, always recomputed, never
   persisted as truth.

---

## 8. Allowed Confidence States

| State | Allowed? | Meaning |
|---|---|---|
| Authoritative truth + high confidence | ✅ | the ideal: corroborated reality |
| Authoritative truth + low confidence | ✅ | valid record, trust-but-verify (e.g. stale progress) |
| Operational truth under unresolved uncertainty | ✅ | reality exists; confidence pending evidence |
| Contradiction held visibly at known confidence | ✅ | layered truth, surfaced (philosophy #8) |
| Low-confidence analytic interpretation | ✅ | exactly what advisory analytics are |
| **Confidence presented as certainty** | ❌ | hides uncertainty — forbidden (A10) |
| **Confidence stored as authoritative state** | ❌ | manufactures truth from interpretation |
| **Confidence auto-gating execution/governance** | ❌ | trust system the platform explicitly rejects |
| **Silent (hidden) contradiction or uncertainty** | ❌ | violates philosophy #8 visibility |

---

## 9. Governance & Audit Expectations

1. **Confidence is interpretive, not an authority act** — it is never approved, signed,
   or recorded as a verdict. Only *evidence and acts* are audited; confidence is read
   from them.
2. **Attribution feeds confidence and must be trustworthy.** Soft client-supplied
   attribution (A18) caps the confidence any observation can earn — you cannot fully
   trust a claim whose actor is unverified.
3. **Analytics must declare their uncertainty** — `false_positive_notes` and
   `data_available: false` are the existing, correct pattern; every interpretation must
   keep carrying them (philosophy #10).
4. **Governance must not launder confidence** — accepting a claim does not retroactively
   make weak evidence strong; the audit trail must still show what evidence existed at
   acceptance.
5. **Uncertainty must remain queryable** — like contradiction (reconciliation §9),
   confidence-relevant gaps (missing report, missing inspection, stale cache) must be
   visible, not silently smoothed over.

---

## 10. Resolved Questions

1. **Can low-confidence truth still be operationally valid?** **Yes.** Truth (DB state)
   is authoritative regardless of confidence; low confidence means "trust less / seek
   corroboration," not "invalid." Execution still happened.
2. **Can high-confidence observations still be wrong?** **Yes.** Confidence is not
   certainty; well-evidenced claims can still misrepresent reality. Confidence is
   fallible interpretation.
3. **Does approval increase confidence or only governance acceptance?** It **increases
   confidence only when it adds genuine corroboration** (authority validating against
   evidence). Bypassable/rubber-stamp approval adds **only acceptance**, not confidence
   (A15).
4. **Can contradictory evidence coexist indefinitely?** **Yes, if surfaced** (layered
   truth). But a **high-confidence** contradiction should escalate, not persist
   silently; indefinite silent coexistence is forbidden.
5. **Can missing evidence reduce confidence without invalidating execution?** **Yes.**
   Absence of evidence lowers confidence but does not undo execution truth (axiom #3).
6. **Can analytics produce low-confidence interpretations?** **Yes — by design.**
   `false_positive_notes`, thresholds, and `data_available: false` *are* declared
   low/qualified confidence. Analytics are advisory, lowest precedence.
7. **Can operational truth exist under uncertainty?** **Yes.** Truth and confidence are
   orthogonal — the DB record is truth; uncertainty is about how well it is trusted to
   reflect reality.
8. **Which layer owns confidence interpretation?** **No single owner, and it is never
   authoritative state.** Confidence is a **cross-cutting interpretive property** read by
   the analytics/interpretation layer (advisory), informed by governance corroboration
   and lineage. It must never become a stored, authoritative, or auto-gating value
   (philosophy #9/#10).

---

## 11. Future Runtime Stabilization Implications

Deltas between this contract and the runtime — **boundaries, not built here**:

1. **Replace "confidence theater" with grounded confidence.** The
   `decision_support` high/medium/low labels should either be tied to real evidence
   factors (§2) or relabeled as priority heuristics, not "confidence" (A10).
2. **Expose freshness/staleness** alongside derived values (progress) so consumers see
   derived-confidence, not a bare number (A3).
3. **Make attribution server-derived** so observations can earn full confidence (A18).
4. **Surface confidence-relevant gaps** (missing report/inspection, open blocker at
   approval) as visible qualifiers, never auto-actions (A5/A15).
5. **Read confidence from lineage**, never store it — corroboration and freshness come
   from the event ledger, recomputed, never persisted as truth.
6. **Resolve ambiguity before labeling confidence** — define "done" (A17) and readiness
   (A4); a confidence label on an undefined concept is meaningless.

Each lives within existing analytics/governance ownership — none requires a scoring
engine, probabilistic model, or trust system. Stabilizing the *meaning* of confidence
first is what prevents the platform from later bolting on a number that pretends to
know more than the evidence does.

---

## 12. Bottom line

Confidence in BetavanX is **not a score and not truth** — it is the qualitative,
evidence-based trustworthiness of a claim about reality, read from actor authority,
evidence, consistency, freshness, lineage, and governance validation. Authoritatively:
**truth and confidence are orthogonal** (valid truth can be low-confidence; high
confidence can be wrong); **approval adds acceptance, and only adds confidence when it
adds corroboration**; **missing evidence lowers confidence without invalidating
execution**; **analytics are inherently low/qualified confidence and must keep saying
so**; and **confidence must never be stored, made authoritative, or allowed to
auto-gate.** The runtime today mostly lacks confidence semantics and in one place fakes
them (the high/medium/low labels). Naming how confidence behaves — without computing it
— is what lets BetavanX become evidence-aware without becoming the heuristic theater its
own philosophy (#10) warns against.

# BetavanX — Controlled Real-World Pilot Playbook (Stage 25)

Operational validation with 1–3 real projects, four pilot roles, and repeated daily usage. **No feature expansion or UI redesign** during the pilot.

---

## Pilot roles

| Role | Username / password | Primary tasks |
| --- | --- | --- |
| admin | `admin` / `admin` | Create projects, planning chain, membership grants |
| supervisor | `supervisor` / `supervisor` | Assign work orders, approve steps, review dashboard |
| worker | `worker` / `worker` | Submit daily reports on assigned work |
| investor | `investor` / `investor` | Read-only dashboard and runtime visibility |

Change passwords before any external pilot. Seed users via `seed_platform_users.py` or first login (idempotent seed).

---

## Recommended operational flow (validate in order)

1. **Planning** — Console → create project, WBS, location, activity, workflow step, work order.
2. **Execution** — Assign work order to workflow step (supervisor/admin).
3. **Daily reporting** — Worker submits report against assigned work order.
4. **Approval** — Supervisor approves workflow step (watch for 409 on stale UI).
5. **Runtime visibility** — Overview KPIs, activity instance detail, execution work-order list.
6. **Dashboard review** — Investor reads summary; admin/supervisor refresh after mutations.

Record friction in **Pilot feedback** on Overview (or `POST /pilot/feedback`).

---

## Deployment (production-like)

```bash
cp .env.docker.example .env.docker
docker compose --env-file .env.docker up --build
```

| Check | Command |
| --- | --- |
| Liveness | `curl http://localhost:8000/health/live` |
| Readiness | `curl http://localhost:8000/health` |
| Automated smoke | `PYTHONPATH=. python backend/scripts/stage25_deployment_validation.py` |
| Timed vertical slice | `RUN_POSTGRES_VALIDATION=true` env + `stage25_controlled_pilot_simulation.py` |
| Metrics summary | `python backend/scripts/stage25_pilot_metrics.py` |

Remote stack: set `PILOT_DEPLOY_BASE_URL=http://your-host:8000`.

---

## Pilot metrics to capture manually

| Metric | How |
| --- | --- |
| Time to create workflow | Stopwatch: project → step → WO → assign |
| Time to submit report | Worker path from login to 201 on daily report |
| Approval latency | Supervisor approve after worker submit |
| Dashboard load | Overview first paint + KPI refresh (30s poll) |
| User errors | Count 4xx/409 in browser network or API logs |
| Conflicts | 409 responses — note if user retried without refresh |

Automated baseline: `STAGE25_METRICS_PATH=./data/stage25_metrics.json python backend/scripts/stage25_controlled_pilot_simulation.py`

---

## Feedback capture

- **UI:** Dashboard → Overview → Pilot feedback card.
- **API:** `POST /pilot/feedback` (authenticated).
- **Storage:** `data/pilot_feedback.jsonl` (override with `PILOT_FEEDBACK_PATH`).

Categories: `confusion`, `blocker`, `missing_flow`, `ux_pain`, `gap`, `other`.

---

## Session reliability checks

- [ ] Same user, 2+ hour session — token still valid; refresh pages.
- [ ] Submit two reports same day — note duplicate/conflict behavior.
- [ ] Switch project in header — lists and KPIs match selected project.
- [ ] Worker on Project A cannot open Project B runtime (403).
- [ ] Restart `docker compose restart backend` — login and list projects recover.

---

## Exit criteria

- All four roles complete the flow at least once per project.
- No unexplained 500s during pilot week.
- Feedback JSONL has ≥1 entry per active participant.
- `stage-25-controlled-pilot-report.md` updated with human notes from the pilot.

Stop after Stage 25; Stage 26 addresses prioritized blockers only.

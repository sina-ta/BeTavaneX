# Live Pilot Analytics Playbook (Stage 27)

Lightweight adoption intelligence — no third-party analytics stack.

## Data sources

| File / API | Captures |
| --- | --- |
| `data/operational_usage.jsonl` | Page views, session starts (frontend `UsageRecorder`) |
| `data/operational_audit.jsonl` | Mutations (reports, approvals, planning — mirrored from audit log) |
| `data/pilot_feedback.jsonl` | Qualitative friction (Stage 25) |
| `GET /analytics/adoption-summary` | Aggregated snapshot (admin + supervisor) |

## Operator cadence

1. Run pilot week with Docker + Postgres; four roles active daily.
2. Review **Pilot adoption snapshot** on Overview (admin/supervisor).
3. Weekly CLI export:

```bash
PYTHONPATH=. python backend/scripts/stage27_adoption_analytics.py
```

4. Correlate bottleneck hints with `pilot_feedback.jsonl` categories.

## Environment variables

| Variable | Default |
| --- | --- |
| `OPERATIONAL_USAGE_PATH` | `data/operational_usage.jsonl` |
| `OPERATIONAL_AUDIT_JSONL_PATH` | `data/operational_audit.jsonl` |
| `PILOT_FEEDBACK_PATH` | `data/pilot_feedback.jsonl` |

## Privacy

- No third-party trackers.
- Usernames stored in JSONL for pilot cohort only — rotate files between pilots.

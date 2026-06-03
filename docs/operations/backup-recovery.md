# BetavanX — Backup & Recovery (Operational)

Lightweight PostgreSQL survivability for Phase 1 deployments. No enterprise DR stack.

---

## Scope

| Asset | Tool | RPO (pilot) | RTO (pilot) |
| --- | --- | --- | --- |
| PostgreSQL data | `pg_dump` / `pg_restore` | 24h (daily backup) | 1–2h manual |
| Alembic revision | `alembic_version` table | Same as DB | Same as DB |
| Application config | Secret manager / `.env` | N/A | Minutes |

---

## Backup flow

### Docker Compose (local / staging)

```bash
docker compose exec postgres pg_dump -U betavanx_app -Fc betavanx_dev > backups/betavanx_$(date +%Y%m%d).dump
```

### Bare metal / managed Postgres

```bash
pg_dump "$DATABASE_URL" -Fc -f backups/betavanx_$(date +%Y%m%d).dump
```

**Schedule (recommended):**

- Staging: daily automated dump, retain 7 days
- Production: daily dump + weekly off-site copy

---

## Restore flow

```bash
# Stop API to prevent writes
docker compose stop backend

# Drop/recreate database (destructive)
docker compose exec postgres psql -U betavanx_app -c "DROP DATABASE IF EXISTS betavanx_dev;"
docker compose exec postgres psql -U betavanx_app -c "CREATE DATABASE betavanx_dev;"

# Restore
docker compose exec -T postgres pg_restore -U betavanx_app -d betavanx_dev < backups/betavanx_YYYYMMDD.dump

# Re-apply migrations if needed
docker compose run --rm backend alembic -c backend/alembic.ini upgrade head
docker compose start backend
```

Verify:

```bash
PYTHONPATH=. python backend/scripts/stage23_deployment_verification.py
DEPLOY_VERIFY_BASE_URL=http://localhost:8000 python backend/scripts/stage23_deployment_verification.py
```

---

## Migration recovery

| Scenario | Action |
| --- | --- |
| Migration failed mid-upgrade | Fix SQL, `alembic downgrade -1`, redeploy |
| DB ahead of code | Deploy matching code tag, or downgrade Alembic |
| Greenfield | `phase1_init_schema.py` then `alembic upgrade head` |

Production startup with `REQUIRE_ALEMBIC_HEAD=true` blocks API boot when revision mismatch.

---

## Rollback strategy

1. Stop traffic to new API revision
2. Restore previous container image tag
3. If schema changed: `alembic downgrade` to previous revision **or** restore pre-migration dump
4. Run `stage23_deployment_verification.py`
5. Re-enable traffic

**Rule:** never downgrade schema without a backup taken immediately before upgrade.

---

## Operational checklist

- [ ] Backup script tested monthly
- [ ] Restore drill documented with elapsed time
- [ ] `BETAVANX_AUTH_SECRET` backed up in secret manager (not in dump)
- [ ] Volume snapshots for Docker Postgres in staging

# 0002 — Operational Intelligence Foundation

## Status

Accepted — 2026-05-24

## Context

BetavanX completed enterprise architecture stabilization. The next phase
requires operational intelligence infrastructure without feature explosion
or premature AI integration.

## Decision

Introduce operational intelligence in layered foundations:

1. **API-only frontend communication** through `lib/api/client.ts`
2. **Validation architecture** aligned with FastAPI/Pydantic schemas
3. **Unified severity system** for operational status interpretation
4. **Chart wrappers** using lightweight SVG sparklines (no chart library yet)
5. **KPI history tracking** via `kpi_history` table and `analytics_service`
6. **Worker intelligence service** for productivity and attendance scoring
7. **Recommendation engine v2** using modular rule evaluators

## Architecture

```plaintext
page → hooks → lib/api → backend router → service → repository → database
```

Recommendation flow:

```plaintext
RecommendationContext → evaluate_rules() → build_recommendation_payload()
```

Analytics flow:

```plaintext
dashboard build → record_dashboard_kpis() → kpi_history → trend aggregation
```

## Consequences

- Dashboard responses now include `trends`
- Recommendations include `severity`, `factors`, and `explanation`
- Worker endpoints expose `/workers/analytics` and `/workers/{id}/intelligence`
- Chart components are architecture-ready placeholders for future analytics depth

## Deferred

- JWT authentication implementation
- AI/ML recommendation models
- WebSocket realtime updates
- External charting libraries

"use client";

import { useCallback } from "react";

import { getExecutiveVisibility } from "@/lib/api/phase1/analytics";
import type { ExecutiveVisibility } from "@/lib/api/phase1/analytics";
import { canViewExecutiveVisibility } from "@/lib/auth/role-policy";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import CompactCard from "@/components/layout/primitives/CompactCard";

const PORTFOLIO_STYLE: Record<string, string> = {
  HEALTHY: "#22c55e",
  STABLE: "#3b82f6",
  CAUTION: "#eab308",
  CRITICAL: "#ef4444",
  UNKNOWN: "#94a3b8",
};

const ATTENTION_STYLE: Record<string, string> = {
  immediate: "#ef4444",
  planned: "#eab308",
  monitor: "#3b82f6",
  stable: "#22c55e",
};

export default function ExecutiveVisibilityPanel() {
  if (!canViewExecutiveVisibility()) {
    return null;
  }

  const fetchExecutive = useCallback(() => getExecutiveVisibility(), []);
  const { status, data, error, reload } =
    useAsyncData<ExecutiveVisibility>(fetchExecutive);

  return (
    <CompactCard title="Executive operational awareness">
      {status === "loading" && (
        <p className="page-subtitle">Compressing portfolio signals…</p>
      )}
      {status === "error" && (
        <p className="page-subtitle">
          Could not load executive visibility.{" "}
          <button type="button" className="button-ghost" onClick={reload}>
            Retry
          </button>
          {error && ` (${error})`}
        </p>
      )}
      {data && <ExecutiveBody data={data} />}
    </CompactCard>
  );
}

function ExecutiveBody({ data }: { data: ExecutiveVisibility }) {
  const band = data.portfolio_health.overall_band;
  const color = PORTFOLIO_STYLE[band] ?? PORTFOLIO_STYLE.UNKNOWN;

  return (
    <div className="flex flex-col gap-4">
      <p className="page-subtitle">
        <span style={{ color, fontWeight: 600 }}>Portfolio {band}</span>
        {" · "}
        {data.portfolio_health.projects_analyzed} project(s) · maturity{" "}
        {data.portfolio_health.maturity_band} · capacity{" "}
        {data.portfolio_health.capacity_band}
      </p>
      <p className="page-subtitle">{data.executive_summary}</p>
      <p className="page-subtitle">{data.portfolio_health.summary}</p>

      {!data.data_available && (
        <p className="page-subtitle">
          Full portfolio analysis requires PostgreSQL and accessible projects.
        </p>
      )}

      {data.strategic_attention.length > 0 && (
        <div>
          <strong style={{ color: "#e2e8f0" }}>Strategic attention</strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {data.strategic_attention.map((line) => (
              <li key={line} className="planning-list-item page-subtitle">
                {line}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.leadership_priorities.length > 0 && (
        <details open>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Leadership priorities
          </summary>
          <ol className="planning-list">
            {data.leadership_priorities.map((p) => (
              <li key={p.rank} className="planning-list-item page-subtitle">
                <span
                  style={{
                    color: ATTENTION_STYLE[p.attention_level] ?? "#94a3b8",
                    fontWeight: 600,
                    marginRight: 6,
                  }}
                >
                  {p.attention_level}
                </span>
                <strong>{p.concern}</strong> — {p.suggested_focus}
              </li>
            ))}
          </ol>
        </details>
      )}

      {data.trend_narratives.length > 0 && (
        <details>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Execution trend narratives
          </summary>
          <ul className="planning-list">
            {data.trend_narratives.map((n) => (
              <li key={n.narrative_id} className="planning-list-item page-subtitle">
                <em>{n.trend_direction}</em> — {n.message}
              </li>
            ))}
          </ul>
        </details>
      )}

      {data.strategic_risks.length > 0 && (
        <details>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Strategic operational risks
          </summary>
          <ul className="planning-list">
            {data.strategic_risks.map((r) => (
              <li key={r.signal_type} className="planning-list-item page-subtitle">
                {r.message}
              </li>
            ))}
          </ul>
        </details>
      )}

      {data.pressure_indicators.length > 0 && (
        <details>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Organizational pressure
          </summary>
          <ul className="planning-list">
            {data.pressure_indicators.map((p) => (
              <li key={p.indicator_type} className="planning-list-item page-subtitle">
                {p.message}
              </li>
            ))}
          </ul>
        </details>
      )}

      {data.portfolio_health.deteriorating_project_codes.length > 0 && (
        <p className="page-subtitle">
          Hotspots: {data.portfolio_health.deteriorating_project_codes.join(", ")}
          {data.portfolio_health.stable_project_codes.length > 0 && (
            <>
              {" "}
              · Stable zones:{" "}
              {data.portfolio_health.stable_project_codes.join(", ")}
            </>
          )}
        </p>
      )}
    </div>
  );
}

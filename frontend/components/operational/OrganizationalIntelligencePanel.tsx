"use client";

import { useCallback } from "react";

import { getOrganizationalIntelligence } from "@/lib/api/phase1/analytics";
import type { OrganizationalIntelligence } from "@/lib/api/phase1/analytics";
import { canViewOrganizationalIntelligence } from "@/lib/auth/role-policy";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import CompactCard from "@/components/layout/primitives/CompactCard";

const MATURITY_STYLE: Record<string, string> = {
  ESTABLISHED: "#22c55e",
  DEVELOPING: "#3b82f6",
  EMERGING: "#eab308",
  STRAINED: "#ef4444",
  UNKNOWN: "#94a3b8",
};

const CAPACITY_STYLE: Record<string, string> = {
  BALANCED: "#22c55e",
  PRESSURED: "#eab308",
  SATURATED: "#ef4444",
  UNKNOWN: "#94a3b8",
};

export default function OrganizationalIntelligencePanel() {
  if (!canViewOrganizationalIntelligence()) {
    return null;
  }

  const fetchOrg = useCallback(() => getOrganizationalIntelligence(), []);
  const { status, data, error, reload } =
    useAsyncData<OrganizationalIntelligence>(fetchOrg);

  return (
    <CompactCard title="Organizational execution intelligence">
      {status === "loading" && (
        <p className="page-subtitle">Analyzing cross-project patterns…</p>
      )}
      {status === "error" && (
        <p className="page-subtitle">
          Could not load organizational intelligence.{" "}
          <button type="button" className="button-ghost" onClick={reload}>
            Retry
          </button>
          {error && ` (${error})`}
        </p>
      )}
      {data && <OrgBody data={data} />}
    </CompactCard>
  );
}

function OrgBody({ data }: { data: OrganizationalIntelligence }) {
  const matColor = MATURITY_STYLE[data.maturity_band] ?? MATURITY_STYLE.UNKNOWN;
  const capColor = CAPACITY_STYLE[data.capacity_band] ?? CAPACITY_STYLE.UNKNOWN;

  return (
    <div className="flex flex-col gap-4">
      <p className="page-subtitle">
        <span style={{ color: matColor, fontWeight: 600, marginRight: 8 }}>
          Maturity {data.maturity_band}
        </span>
        {data.maturity_score !== null && <> ({data.maturity_score}/100) · </>}
        {data.projects_analyzed} project(s) analyzed
      </p>
      <p className="page-subtitle">{data.maturity_summary}</p>
      <p className="page-subtitle">
        <span style={{ color: capColor, fontWeight: 600 }}>Capacity {data.capacity_band}</span>
        {" — "}
        {data.capacity_summary}
      </p>

      {!data.data_available && (
        <p className="page-subtitle">
          Full cross-project analysis requires PostgreSQL.
        </p>
      )}

      {data.organizational_attention.length > 0 && (
        <div>
          <strong style={{ color: "#e2e8f0" }}>Organizational attention</strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {data.organizational_attention.map((line) => (
              <li key={line} className="planning-list-item page-subtitle">
                {line}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.maturity_components.length > 0 && (
        <details>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Execution maturity components
          </summary>
          <ul className="planning-list">
            {data.maturity_components.map((c) => (
              <li key={c.factor} className="planning-list-item page-subtitle">
                <strong>{c.factor}</strong> ({c.score}/100) — {c.detail}
              </li>
            ))}
          </ul>
        </details>
      )}

      {data.supervisor_trends.length > 0 && (
        <details>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Supervisor effectiveness trends (operational)
          </summary>
          <ul className="planning-list">
            {data.supervisor_trends.map((t) => (
              <li key={t.username} className="planning-list-item page-subtitle">
                <strong>{t.username}</strong> ({t.role}) — {t.observation}
              </li>
            ))}
          </ul>
        </details>
      )}

      {data.project_snapshots.length > 0 && (
        <details>
          <summary className="compact-card__title" style={{ cursor: "pointer" }}>
            Multi-project snapshots
          </summary>
          <ul className="planning-list">
            {data.project_snapshots.map((p) => (
              <li key={p.project_id} className="planning-list-item page-subtitle">
                <strong>{p.project_code}</strong> — health {p.health_band}, pressure{" "}
                {p.coordination_pressure} · blockers {p.open_blockers} · approvals{" "}
                {p.pending_approvals}
              </li>
            ))}
          </ul>
        </details>
      )}

      <SignalBlock title="Cross-project findings" items={data.cross_project_findings} />
      <SignalBlock title="Organizational bottlenecks" items={data.organizational_bottlenecks} />
      <SignalBlock title="Operational culture indicators" items={data.culture_indicators} />
      <SignalBlock
        title="Multi-project coordination"
        items={data.multi_project_coordination}
      />
    </div>
  );
}

function SignalBlock({
  title,
  items,
}: {
  title: string;
  items: OrganizationalIntelligence["cross_project_findings"];
}) {
  if (items.length === 0) {
    return null;
  }
  return (
    <details>
      <summary className="compact-card__title" style={{ cursor: "pointer" }}>
        {title}
      </summary>
      <ul className="planning-list">
        {items.map((s) => (
          <li key={s.signal_type} className="planning-list-item page-subtitle">
            {s.message}
          </li>
        ))}
      </ul>
    </details>
  );
}

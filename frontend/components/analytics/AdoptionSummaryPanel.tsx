"use client";

import { useCallback } from "react";

import { getAdoptionSummary } from "@/lib/api/phase1/analytics";
import type { AdoptionSummary } from "@/lib/api/phase1/analytics";
import { canViewAdoptionSummary } from "@/lib/auth/role-policy";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import CompactCard from "@/components/layout/primitives/CompactCard";

export default function AdoptionSummaryPanel() {
  if (!canViewAdoptionSummary()) {
    return null;
  }

  const fetchSummary = useCallback(() => getAdoptionSummary(), []);
  const { status, data, error, reload } =
    useAsyncData<AdoptionSummary>(fetchSummary);

  return (
    <CompactCard title="Pilot adoption snapshot">
      {status === "loading" && (
        <p className="page-subtitle">Loading adoption analytics…</p>
      )}
      {status === "error" && (
        <p className="page-subtitle">
          Could not load analytics.{" "}
          <button type="button" className="button-ghost" onClick={reload}>
            Retry
          </button>
          {error && ` (${error})`}
        </p>
      )}
      {data && <AdoptionSummaryBody summary={data} />}
    </CompactCard>
  );
}

function AdoptionSummaryBody({ summary }: { summary: AdoptionSummary }) {
  const topPages = Object.entries(summary.usage.page_views).slice(0, 5);
  const hints = summary.bottleneck_hints;

  return (
    <div className="flex flex-col gap-4">
      <p className="page-subtitle">
        Distinct users: {summary.usage.distinct_users} · Usage events:{" "}
        {summary.usage.event_count} · Audit records:{" "}
        {summary.mutations.audit_record_count}
      </p>
      <p className="page-subtitle">
        Reports (audit): {summary.mutations.daily_report_actions} · Approvals:{" "}
        {summary.mutations.approval_actions} · Multi-day users:{" "}
        {summary.retention.users_with_multi_day_activity}
      </p>
      {Object.keys(summary.db_snapshot).length > 0 && (
        <p className="page-subtitle">
          DB totals — projects: {summary.db_snapshot.projects_total ?? 0},
          reports: {summary.db_snapshot.daily_reports_total ?? 0}, approvals:{" "}
          {summary.db_snapshot.approvals_total ?? 0}
        </p>
      )}
      {topPages.length > 0 && (
        <div>
          <strong className="text-emphasis">Top pages</strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {topPages.map(([path, count]) => (
              <li key={path} className="planning-list-item">
                {path} — {count}
              </li>
            ))}
          </ul>
        </div>
      )}
      {hints.length > 0 && (
        <div>
          <strong className="text-emphasis">Bottleneck hints</strong>
          <ul className="planning-list" style={{ marginTop: 8 }}>
            {hints.map((hint) => (
              <li key={hint} className="planning-list-item">
                {hint}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

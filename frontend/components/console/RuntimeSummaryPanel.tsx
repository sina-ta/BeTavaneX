"use client";

import { useCallback } from "react";

import { getProjectDashboard } from "@/lib/api/phase1/runtime";
import { toNumber } from "@/lib/api/phase1/types";
import type { ProjectDashboard } from "@/lib/api/phase1/types";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import KpiCard from "@/components/KpiCard";
import ProgressBar from "@/components/ui/ProgressBar";
import KPIGrid from "@/components/layout/primitives/KPIGrid";
import CompactCard from "@/components/layout/primitives/CompactCard";

/**
 * Live project runtime summary. Parent remounts via `key` after mutations to
 * refresh; a manual reload button is also provided.
 */
export default function RuntimeSummaryPanel({
  projectId,
}: {
  projectId: string;
}) {
  const fetchDashboard = useCallback(
    () => getProjectDashboard(projectId),
    [projectId]
  );

  const { status, data, error, reload } =
    useAsyncData<ProjectDashboard>(fetchDashboard);

  return (
    <CompactCard title="Live Runtime Summary">
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <button
          type="button"
          className="button-ghost"
          onClick={reload}
          style={{ alignSelf: "flex-start" }}
        >
          ↻ Refresh
        </button>

        {status === "loading" && (
          <div className="panel-placeholder">
            <span>Loading runtime summary…</span>
          </div>
        )}

        {status === "error" && (
          <div className="panel-placeholder">
            <span>{error ?? "Failed to load summary"}</span>
          </div>
        )}

        {data && (
          <>
            <KPIGrid columns={2}>
              <KpiCard
                title="Project Progress"
                value={`${toNumber(data.project_progress).toFixed(1)}%`}
                progress={toNumber(data.project_progress)}
              />
              <KpiCard
                title="Activity Instances"
                value={data.activity_instance_count}
              />
              <KpiCard
                title="Workflow Steps"
                value={data.workflow_step_count}
              />
              <KpiCard title="Work Orders" value={data.work_order_count} />
            </KPIGrid>

            <ProgressBar value={toNumber(data.project_progress)} />
          </>
        )}
      </div>
    </CompactCard>
  );
}

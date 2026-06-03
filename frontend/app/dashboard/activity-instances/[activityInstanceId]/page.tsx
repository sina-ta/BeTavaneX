"use client";

import { use, useCallback, useState } from "react";
import Link from "next/link";

import {
  approveWorkflowStep,
  getActivityInstanceRuntime,
} from "@/lib/api/phase1/runtime";
import { toNumber } from "@/lib/api/phase1/types";
import type {
  ActivityInstanceRuntimeView,
  WorkflowStep,
  WorkflowStepOperationalRead,
} from "@/lib/api/phase1/types";
import { canApproveSteps } from "@/lib/auth/role-policy";
import { useWorkspace } from "@/lib/context/WorkspaceContext";
import { useWorkflowSteps } from "@/lib/hooks/usePhase1Lists";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import { useRuntimePolling } from "@/lib/hooks/useRuntimePolling";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import KpiCard from "@/components/KpiCard";
import StatusBadge from "@/components/ui/StatusBadge";
import ProgressBar from "@/components/ui/ProgressBar";
import PageHeader from "@/components/ui/PageHeader";
import CompactCard from "@/components/layout/primitives/CompactCard";
import KPIGrid from "@/components/layout/primitives/KPIGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";

type ActivityInstancePageProps = {
  params: Promise<{
    activityInstanceId: string;
  }>;
};

export default function ActivityInstanceRuntimePage({
  params,
}: ActivityInstancePageProps) {
  const { activityInstanceId } = use(params);

  const fetchView = useCallback(
    () => getActivityInstanceRuntime(activityInstanceId),
    [activityInstanceId]
  );

  const { status, data, error, reload } =
    useAsyncData<ActivityInstanceRuntimeView>(fetchView);
  const { data: operationalSteps, reload: reloadSteps } =
    useWorkflowSteps(activityInstanceId);

  useRuntimePolling(() => {
    reload();
    void reloadSteps();
  }, status === "success", 45_000);

  const operationalByStepId = new Map<string, WorkflowStepOperationalRead>(
    (operationalSteps?.items ?? []).map((row) => [
      row.workflow_step.id,
      row,
    ])
  );

  return (
    <AsyncPageContent
      status={status}
      data={data}
      error={error}
      loadingTitle="Activity Instance"
      loadingSubtitle="Loading activity runtime view…"
      loadingMessage="Loading workflow steps & progress…"
      emptyTitle="Activity instance not found"
      onRetry={reload}
      isEmpty={(view) => view.activity_instance === null}
    >
      {(view) => {
        const activity = view.activity_instance;
        const summary = view.progress_summary;
        const activityProgress = toNumber(
          summary.activity_instance_progress
        );

        return (
          <SectionContainer>
            <PageHeader
              title={activity ? activity.name : "Activity Instance"}
              subtitle={
                activity
                  ? `Code ${activity.code} · status ${activity.status}`
                  : undefined
              }
              eyebrow="Activity Runtime"
            />

            <div
              style={{ display: "flex", flexWrap: "wrap", gap: 8 }}
            >
              <Link
                href="/dashboard/overview"
                className="button-ghost"
              >
                ← Command center
              </Link>
              <Link
                href="/dashboard/console/execution"
                className="button-ghost"
              >
                Execution console →
              </Link>
            </div>

            <KPIGrid columns={3}>
              <KpiCard
                title="Activity Progress"
                value={`${activityProgress.toFixed(1)}%`}
                progress={activityProgress}
              />
              <KpiCard
                title="Workflow Steps"
                value={view.workflow_steps.length}
                footer="Execution-reality steps"
              />
              <section className="kpi-card">
                <span className="kpi-title">Status</span>
                {activity ? (
                  <StatusBadge status={activity.status} />
                ) : (
                  <span className="kpi-value">—</span>
                )}
              </section>
            </KPIGrid>

            <CompactCard title="Workflow Steps">
              {view.workflow_steps.length === 0 ? (
                <div className="panel-placeholder">
                  <span>No workflow steps for this activity.</span>
                </div>
              ) : (
                <div className="planning-list">
                  {view.workflow_steps.map((step) => (
                    <WorkflowStepCard
                      key={step.id}
                      step={step}
                      operational={operationalByStepId.get(step.id)}
                      progress={toNumber(
                        summary.workflow_step_progress[step.id] ??
                          step.progress_percent
                      )}
                      onApproved={reload}
                    />
                  ))}
                </div>
              )}
            </CompactCard>
          </SectionContainer>
        );
      }}
    </AsyncPageContent>
  );
}

// ---------------------------------------------------------------------------

function WorkflowStepCard({
  step,
  operational,
  progress,
  onApproved,
}: {
  step: WorkflowStep;
  operational?: WorkflowStepOperationalRead;
  progress: number;
  onApproved: () => void;
}) {
  const workspace = useWorkspace();
  const [approving, setApproving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const assignments = workspace.assignmentsForStep(step.id);
  const approvals =
    operational?.approvals ?? workspace.approvalsForStep(step.id);
  const blockers = operational?.blockers ?? [];
  const mayApprove = canApproveSteps();

  async function handleApprove() {
    if (approving) {
      return;
    }
    setApproving(true);
    setError(null);
    try {
      const approval = await approveWorkflowStep(step.id, {
        approval_type: "FINAL",
        approval_date: new Date().toISOString().slice(0, 10),
        expected_workflow_step_updated_at:
          operational?.workflow_step.updated_at ?? step.updated_at,
      });
      workspace.addApproval(approval);
      onApproved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Approval failed");
    } finally {
      setApproving(false);
    }
  }

  return (
    <div className="planning-list-item">
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
        }}
      >
        <strong>{step.name}</strong>
        <StatusBadge status={step.status} />
      </div>
      <span className="page-subtitle">
        Code {step.code}
        {step.ready ? " · ready" : ""}
      </span>
      <ProgressBar value={progress} />

      {(approvals.length > 0 || blockers.length > 0) && (
        <div className="planning-list" style={{ marginTop: 8 }}>
          {approvals.map((approval) => (
            <div
              key={approval.id}
              className="planning-list-item"
              style={{ background: "rgba(34,197,94,0.08)" }}
            >
              <span className="page-subtitle">
                Approval {approval.approval_type} · {approval.status}
              </span>
            </div>
          ))}
          {blockers.map((blocker) => (
            <div
              key={blocker.id}
              className="planning-list-item"
              style={{ background: "rgba(248,113,113,0.08)" }}
            >
              <span className="page-subtitle">
                Blocker {blocker.severity}: {blocker.title} ({blocker.status})
              </span>
            </div>
          ))}
        </div>
      )}

      {assignments.length > 0 && (
        <div className="planning-list" style={{ marginTop: 8 }}>
          {assignments.map((assignment) => {
            const workOrder = workspace.workOrders.find(
              (w) => w.id === assignment.work_order_id
            );
            const reports = workspace.dailyReportsForWorkOrder(
              assignment.work_order_id
            );

            return (
              <div
                key={assignment.id}
                className="planning-list-item"
                style={{ background: "rgba(148,163,184,0.06)" }}
              >
                <span className="page-subtitle">
                  WO{" "}
                  {workOrder
                    ? `${workOrder.work_order_number} — ${workOrder.title}`
                    : assignment.work_order_id}{" "}
                  · weight {toNumber(assignment.execution_weight)}
                </span>
                <span className="page-subtitle">
                  {reports.length} daily report
                  {reports.length === 1 ? "" : "s"}
                </span>
              </div>
            );
          })}
        </div>
      )}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          marginTop: 8,
        }}
      >
        {mayApprove ? (
          <button
            type="button"
            className="button-primary"
            onClick={handleApprove}
            disabled={approving || step.status === "APPROVED"}
          >
            {step.status === "APPROVED"
              ? "Approved"
              : approving
                ? "Approving…"
                : "Approve Step"}
          </button>
        ) : (
          <span className="page-subtitle">Approval not available for your role.</span>
        )}
      </div>

      {error && (
        <p style={{ color: "#f87171", fontSize: 14 }}>{error}</p>
      )}
    </div>
  );
}

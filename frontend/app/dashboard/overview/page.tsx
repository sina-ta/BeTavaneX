"use client";

import { useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { getProjectDashboardSummary } from "@/lib/api/phase1/runtime";
import { toNumber } from "@/lib/api/phase1/types";
import type { ProjectDashboardSummary } from "@/lib/api/phase1/types";
import {
  canAccessOperationalConsole,
  canPlan,
  getPhase1Role,
  isReadOnlyInvestor,
} from "@/lib/auth/role-policy";
import { useProject } from "@/lib/context/ProjectContext";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import { useRuntimePolling } from "@/lib/hooks/useRuntimePolling";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import EntitySelect from "@/components/forms/EntitySelect";
import KpiCard from "@/components/KpiCard";
import PageHeader from "@/components/ui/PageHeader";
import ProgressBar from "@/components/ui/ProgressBar";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import KPIGrid from "@/components/layout/primitives/KPIGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import AdoptionSummaryPanel from "@/components/analytics/AdoptionSummaryPanel";
import ExecutiveVisibilityPanel from "@/components/operational/ExecutiveVisibilityPanel";
import OrganizationalIntelligencePanel from "@/components/operational/OrganizationalIntelligencePanel";
import OperationalAttentionPanel from "@/components/operational/OperationalAttentionPanel";
import OperationalQuickActions from "@/components/operational/OperationalQuickActions";
import PilotFeedbackForm from "@/components/pilot/PilotFeedbackForm";

export default function OverviewPage() {
  const {
    selectedProjectId,
    setSelectedProjectId,
    authorizedProjects,
    projectsStatus,
    refreshAuthorizedProjects,
  } = useProject();

  if (!selectedProjectId) {
    return (
      <ProjectSelector
        projects={authorizedProjects}
        projectsStatus={projectsStatus}
        onSelect={setSelectedProjectId}
        onRefresh={refreshAuthorizedProjects}
      />
    );
  }

  return (
    <RuntimeProjectDashboard
      projectId={selectedProjectId}
      onChangeProject={() => setSelectedProjectId(null)}
    />
  );
}

function ProjectSelector({
  projects,
  projectsStatus,
  onSelect,
  onRefresh,
}: {
  projects: { id: string; code: string; name: string }[];
  projectsStatus: string;
  onSelect: (projectId: string) => void;
  onRefresh: () => Promise<void>;
}) {
  const role = getPhase1Role();

  return (
    <SectionContainer>
      <PageHeader
        title="Project Command Center"
        subtitle="Select an authorized project to load its runtime dashboard."
        eyebrow="Command Center"
      />
      <ExecutiveVisibilityPanel />
      <OrganizationalIntelligencePanel />

      <CompactCard title="Your Projects">
        {projectsStatus === "loading" && (
          <p className="page-subtitle">Loading authorized projects…</p>
        )}
        {projectsStatus === "error" && (
          <p className="page-subtitle">
            Could not load projects.{" "}
            <button type="button" className="button-ghost" onClick={onRefresh}>
              Retry
            </button>
          </p>
        )}
        {projectsStatus === "ready" && projects.length === 0 && (
          <p className="page-subtitle">
            No authorized projects yet.
            {canPlan(role) && (
              <>
                {" "}
                <Link
                  href="/dashboard/console"
                  className="text-link"
                >
                  Create one in the Operational Console
                </Link>
                .
              </>
            )}
          </p>
        )}
        {projects.length > 0 && (
          <form
            className="flex flex-col gap-5"
            onSubmit={(event) => {
              event.preventDefault();
              const select = event.currentTarget.elements.namedItem(
                "project-picker"
              ) as HTMLSelectElement;
              if (select.value) {
                onSelect(select.value);
              }
            }}
          >
            <EntitySelect
              id="project-picker"
              name="project-picker"
              placeholder="Select a project…"
              options={projects.map((project) => ({
                value: project.id,
                label: `${project.code} — ${project.name}`,
              }))}
            />
            <button type="submit" className="button-primary">
              Open Dashboard
            </button>
          </form>
        )}
      </CompactCard>
    </SectionContainer>
  );
}

function RuntimeProjectDashboard({
  projectId,
  onChangeProject,
}: {
  projectId: string;
  onChangeProject: () => void;
}) {
  const router = useRouter();
  const role = getPhase1Role();

  const fetchDashboard = useCallback(
    () => getProjectDashboardSummary(projectId),
    [projectId]
  );

  const { status, data, error, reload } =
    useAsyncData<ProjectDashboardSummary>(fetchDashboard);

  useRuntimePolling(reload, status === "success", 30_000);

  return (
    <AsyncPageContent
      status={status}
      data={data}
      error={error}
      loadingTitle="Project Command Center"
      loadingSubtitle="Loading project runtime dashboard…"
      loadingMessage="Loading operational intelligence…"
      emptyTitle="No dashboard data available"
      onRetry={reload}
    >
      {(dashboard) => {
        const progress = toNumber(dashboard.project_progress);

        return (
          <SectionContainer className="dashboard-command-center">
            <PageHeader
              title="Project Command Center"
              subtitle={`Runtime dashboard · project ${dashboard.project_id}`}
              eyebrow="Command Center"
            />

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              <button
                type="button"
                className="button-ghost"
                onClick={onChangeProject}
              >
                ← Change project
              </button>
              {canAccessOperationalConsole(role) && (
                <Link
                  href={
                    role === "worker"
                      ? "/dashboard/console/execution?focus=report"
                      : "/dashboard/console"
                  }
                  className="button-ghost"
                >
                  Operational Console →
                </Link>
              )}
              <button type="button" className="button-ghost" onClick={reload}>
                Refresh dashboard
              </button>
            </div>

            <OperationalQuickActions />

            <ExecutiveVisibilityPanel />
            <OrganizationalIntelligencePanel />

            <AdoptionSummaryPanel />

            <OperationalAttentionPanel projectId={projectId} />

            <KPIGrid columns={isReadOnlyInvestor(role) ? 3 : 4}>
              <KpiCard
                title="Project Progress"
                value={`${progress.toFixed(1)}%`}
                progress={progress}
                footer="Aggregated execution progress"
              />
              <KpiCard
                title="Activity Instances"
                value={dashboard.activity_instance_count}
                footer="Planned executable activities"
              />
              <KpiCard
                title="Workflow Steps"
                value={dashboard.workflow_step_count}
                footer="Execution-reality steps"
              />
              {!isReadOnlyInvestor(role) && (
                <KpiCard
                  title="Work Orders"
                  value={dashboard.work_order_count}
                  footer="Coordination units"
                />
              )}
            </KPIGrid>

            <DashboardGrid variant="split">
              <CompactCard title="Overall Progress">
                <ProgressBar value={progress} />
              </CompactCard>

              <CompactCard title="Work Orders by Status">
                {dashboard.work_orders_by_status.length === 0 ? (
                  <p className="page-subtitle">No work orders yet.</p>
                ) : (
                  <div className="planning-list">
                    {dashboard.work_orders_by_status.map((row) => (
                      <div key={row.status} className="planning-list-item">
                        <strong>{row.status}</strong>
                        <span className="page-subtitle"> · {row.count}</span>
                      </div>
                    ))}
                  </div>
                )}
              </CompactCard>
            </DashboardGrid>

            <CompactCard title="Activity Instances">
              {dashboard.activity_instances.length === 0 ? (
                <p className="page-subtitle">
                  No activities yet.
                  {canPlan(role) && (
                    <>
                      {" "}
                      <Link
                        href="/dashboard/console/activity"
                        className="text-link"
                      >
                        Create in Operational Console
                      </Link>
                    </>
                  )}
                </p>
              ) : (
                <div className="planning-list">
                  {dashboard.activity_instances.map((activity) => (
                    <Link
                      key={activity.activity_instance_id}
                      href={`/dashboard/activity-instances/${activity.activity_instance_id}`}
                      className="planning-list-item"
                      style={{ display: "block" }}
                    >
                      <strong>
                        {activity.code} — {activity.name}
                      </strong>
                      <span className="page-subtitle">
                        {" "}
                        · {toNumber(activity.progress_percent).toFixed(1)}% ·
                        status {activity.status} →
                      </span>
                    </Link>
                  ))}
                </div>
              )}
            </CompactCard>

            {isReadOnlyInvestor(role) && (
              <CompactCard title="Investor view">
                <p className="page-subtitle">
                  Read-only access. Operational changes are disabled for your
                  role.
                </p>
              </CompactCard>
            )}

            <details className="compact-card" style={{ padding: "var(--card-padding)" }}>
              <summary
                className="compact-card__title"
                style={{ cursor: "pointer", listStyle: "position" }}
              >
                Pilot feedback (optional)
              </summary>
              <div style={{ marginTop: "var(--space-3)" }}>
                <PilotFeedbackForm pagePath="/dashboard/overview" bare />
              </div>
            </details>
          </SectionContainer>
        );
      }}
    </AsyncPageContent>
  );
}

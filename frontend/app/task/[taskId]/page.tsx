"use client";

import { use, useCallback } from "react";
import Link from "next/link";

import { getTaskById } from "@/lib/api/tasks";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import KpiCard from "@/components/KpiCard";
import StatusBadge from "@/components/ui/StatusBadge";
import RecommendationCard from "@/components/RecommendationCard";
import ReportsTable from "@/components/tables/ReportsTable";
import PageHeader from "@/components/ui/PageHeader";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import KPIGrid from "@/components/layout/primitives/KPIGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import type { TaskDetail } from "@/types/task";

type TaskDetailPageProps = {
  params: Promise<{
    taskId: string;
  }>;
};

export default function TaskDetailPage({
  params,
}: TaskDetailPageProps) {
  const { taskId } = use(params);
  const numericTaskId = Number(taskId);

  const fetchTask = useCallback(
    () => getTaskById(numericTaskId),
    [numericTaskId]
  );

  const { status, data, error, reload } =
    useAsyncData<TaskDetail>(fetchTask);

  return (
    <AsyncPageContent
      status={status}
      data={data}
      error={error}
      loadingTitle={`Task ${taskId}`}
      loadingSubtitle="Loading task intelligence..."
      loadingMessage="Loading task details..."
      emptyTitle="Task not found"
      onRetry={reload}
      isEmpty={(task) => !task.task_id}
    >
      {(taskData) => (
        <SectionContainer>
          <PageHeader
            title={`Work Unit ${taskData.task_id}`}
            subtitle={`Assigned to ${taskData.assigned_to}`}
            eyebrow="Task Intelligence"
          />

          <Link
            href="/dashboard/daily-work-orders"
            className="text-blue-400 text-xs font-medium hover:underline"
            style={{ marginTop: -4 }}
          >
            ← Work orders
          </Link>

          <KPIGrid>
            <KpiCard
              title="Progress"
              value={`${taskData.progress_percent.toFixed(1)}%`}
            />
            <KpiCard
              title="CPI"
              value={taskData.cpi.toFixed(2)}
            />
            <KpiCard
              title="SPI"
              value={taskData.spi.toFixed(2)}
            />
            <section className="kpi-card">
              <span className="kpi-title">Status</span>
              <StatusBadge status={taskData.alert} />
            </section>
          </KPIGrid>

          <RecommendationCard
            title={taskData.recommendation.title}
            message={taskData.recommendation.action}
            recommendation={taskData.recommendation}
          />

          <DashboardGrid variant="split">
            <CompactCard title="Daily Reports">
              <ReportsTable reports={taskData.reports} />
            </CompactCard>

            <CompactCard title="Execution Lifecycle">
              <div className="panel-placeholder">
                <span className="panel-placeholder-icon">⏱</span>
                <span>Lifecycle timeline — readiness & blockers</span>
              </div>
            </CompactCard>
          </DashboardGrid>
        </SectionContainer>
      )}
    </AsyncPageContent>
  );
}

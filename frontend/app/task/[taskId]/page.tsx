"use client";

import { use, useCallback } from "react";

import { getTaskById } from "@/lib/api/tasks";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import KpiCard from "@/components/KpiCard";
import StatusBadge from "@/components/ui/StatusBadge";
import RecommendationCard from "@/components/RecommendationCard";
import ReportsTable from "@/components/tables/ReportsTable";
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
        <div className="min-h-screen bg-gray-100 p-8">
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-800">
                Task {taskData.task_id}
              </h1>

              <p className="text-gray-500 mt-2">
                Assigned To: {taskData.assigned_to}
              </p>
            </div>

            <div className="grid grid-cols-4 gap-6">
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

              <div className="card">
                <p className="metric-label">Status</p>

                <StatusBadge status={taskData.alert} />
              </div>
            </div>

            <RecommendationCard
              title={taskData.recommendation.title}
              message={taskData.recommendation.action}
              recommendation={taskData.recommendation}
            />

            <ReportsTable reports={taskData.reports} />
          </div>
        </div>
      )}
    </AsyncPageContent>
  );
}

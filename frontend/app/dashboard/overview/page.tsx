"use client";

import { useCallback } from "react";

import { getDashboardData } from "@/lib/api/dashboard";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import DashboardHeader from "@/components/dashboard/DashboardHeader";
import KpiSection from "@/components/dashboard/KpiSection";
import RecommendationSection from "@/components/dashboard/RecommendationSection";
import AnalyticsSection from "@/components/dashboard/AnalyticsSection";
import TrendsSection from "@/components/dashboard/TrendsSection";
import TasksSection from "@/components/dashboard/TasksSection";
import type { DashboardData } from "@/types/dashboard";

const PAGE_TITLE = "Project Overview";
const PAGE_SUBTITLE =
  "Real-time construction performance and project intelligence dashboard";

export default function OverviewPage() {
  const fetchDashboard = useCallback(
    () => getDashboardData(),
    []
  );

  const { status, data, error, reload } =
    useAsyncData<DashboardData>(fetchDashboard);

  return (
    <AsyncPageContent
      status={status}
      data={data}
      error={error}
      loadingTitle={PAGE_TITLE}
      loadingSubtitle={PAGE_SUBTITLE}
      loadingMessage="Loading dashboard..."
      emptyTitle="No dashboard data available"
      onRetry={reload}
    >
      {(dashboardData) => (
        <section className="page-wrapper">
          <DashboardHeader
            title={PAGE_TITLE}
            subtitle={PAGE_SUBTITLE}
          />

          <RecommendationSection
            recommendation={
              dashboardData.tasks[0]?.recommendation
            }
          />

          <KpiSection
            summary={dashboardData.summary}
            trends={dashboardData.trends}
          />

          <TrendsSection trends={dashboardData.trends} />

          <AnalyticsSection
            summary={dashboardData.summary}
          />

          <TasksSection tasks={dashboardData.tasks} />
        </section>
      )}
    </AsyncPageContent>
  );
}

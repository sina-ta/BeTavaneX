"use client";

import { useCallback } from "react";

import { getDashboardData } from "@/lib/api/dashboard";
import { getPrimaryRecommendation } from "@/lib/operational/dashboardSummary";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import RecommendationSection from "@/components/dashboard/RecommendationSection";
import KpiSection from "@/components/dashboard/KpiSection";
import TasksSection from "@/components/dashboard/TasksSection";
import TrendsSection from "@/components/dashboard/TrendsSection";
import AnalyticsSection from "@/components/dashboard/AnalyticsSection";
import PageHeader from "@/components/ui/PageHeader";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import type { DashboardData } from "@/types/dashboard";

const PAGE_TITLE = "Project Overview";
const PAGE_SUBTITLE =
  "Real-time construction operational intelligence";

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
      loadingMessage="Loading operational intelligence..."
      emptyTitle="No dashboard data available"
      onRetry={reload}
    >
      {(dashboardData) => (
        <SectionContainer className="dashboard-command-center">
          <PageHeader
            title={PAGE_TITLE}
            subtitle={PAGE_SUBTITLE}
            eyebrow="Command Center"
          />

          <KpiSection
            summary={dashboardData.summary}
            trends={dashboardData.trends}
          />

          <RecommendationSection
            recommendation={getPrimaryRecommendation(
              dashboardData.tasks
            )}
          />

          <DashboardGrid variant="split">
            <TasksSection tasks={dashboardData.tasks} />

            <div className="dashboard-grid__stack-tight">
              <CompactCard title="Schedule & Cost Trends">
                <TrendsSection trends={dashboardData.trends} />
              </CompactCard>

              <CompactCard title="4D BIM Viewer">
                <div className="panel-placeholder">
                  <span className="panel-placeholder-icon">🏗</span>
                  <span>BIM model overlay — connect viewer</span>
                </div>
              </CompactCard>
            </div>
          </DashboardGrid>

          <CompactCard title="Analytics Engines">
            <AnalyticsSection summary={dashboardData.summary} />
          </CompactCard>
        </SectionContainer>
      )}
    </AsyncPageContent>
  );
}

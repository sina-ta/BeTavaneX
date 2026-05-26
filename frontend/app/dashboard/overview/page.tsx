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
import { useI18n } from "@/i18n/LanguageProvider";
import type { DashboardData } from "@/types/dashboard";

export default function OverviewPage() {
  const { t } = useI18n();
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
      loadingTitle={t("overview_title")}
      loadingSubtitle={t("overview_subtitle")}
      loadingMessage="Loading operational intelligence..."
      emptyTitle="No dashboard data available"
      onRetry={reload}
    >
      {(dashboardData) => (
        <SectionContainer className="dashboard-command-center">
          <PageHeader
            title={t("overview_title")}
            subtitle={t("overview_subtitle")}
            eyebrow={t("eyebrow_command_center")}
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
              <CompactCard
                title={t("overview_schedule_cost_trends")}
              >
                <TrendsSection trends={dashboardData.trends} />
              </CompactCard>

              <CompactCard title={t("overview_bim_viewer")}>
                <div className="panel-placeholder">
                  <span className="panel-placeholder-icon">🏗</span>
                  <span>{t("overview_bim_placeholder")}</span>
                </div>
              </CompactCard>
            </div>
          </DashboardGrid>

          <CompactCard title={t("overview_analytics_engines")}>
            <AnalyticsSection summary={dashboardData.summary} />
          </CompactCard>
        </SectionContainer>
      )}
    </AsyncPageContent>
  );
}

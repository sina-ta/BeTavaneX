"use client";

import { useCallback } from "react";

import { getDashboardData } from "@/lib/api/dashboard";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import PageHeader from "@/components/ui/PageHeader";
import KpiSection from "@/components/dashboard/KpiSection";
import TrendsSection from "@/components/dashboard/TrendsSection";
import AnalyticsSection from "@/components/dashboard/AnalyticsSection";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import type { DashboardData } from "@/types/dashboard";

const PAGE_TITLE = "Performance Analytics";
const PAGE_SUBTITLE =
  "KPI trends, cost performance, and schedule intelligence";

export default function PerformancePage() {
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
      loadingMessage="Loading performance analytics..."
      emptyTitle="No performance data available"
      onRetry={reload}
    >
      {(dashboardData) => (
        <SectionContainer>
          <PageHeader
            title={PAGE_TITLE}
            subtitle={PAGE_SUBTITLE}
            eyebrow="Analytics"
          />

          <KpiSection
            summary={dashboardData.summary}
            trends={dashboardData.trends}
          />

          <DashboardGrid variant="split">
            <CompactCard title="KPI Trends">
              <TrendsSection trends={dashboardData.trends} />
            </CompactCard>

            <CompactCard title="Risk Heatmap">
              <div className="panel-placeholder">
                <span className="panel-placeholder-icon">🌡</span>
                <span>Risk exposure map — connect risk engine</span>
              </div>
            </CompactCard>
          </DashboardGrid>

          <CompactCard title="Engine Analytics">
            <AnalyticsSection summary={dashboardData.summary} />
          </CompactCard>
        </SectionContainer>
      )}
    </AsyncPageContent>
  );
}

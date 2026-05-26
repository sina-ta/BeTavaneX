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
import { useI18n } from "@/i18n/LanguageProvider";
import type { DashboardData } from "@/types/dashboard";

export default function PerformancePage() {
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
      loadingTitle={t("performance_title")}
      loadingSubtitle={t("performance_subtitle")}
      loadingMessage="Loading performance analytics..."
      emptyTitle="No performance data available"
      onRetry={reload}
    >
      {(dashboardData) => (
        <SectionContainer>
          <PageHeader
            title={t("performance_title")}
            subtitle={t("performance_subtitle")}
            eyebrow={t("eyebrow_analytics")}
          />

          <KpiSection
            summary={dashboardData.summary}
            trends={dashboardData.trends}
          />

          <DashboardGrid variant="split">
            <CompactCard title={t("performance_kpi_trends")}>
              <TrendsSection trends={dashboardData.trends} />
            </CompactCard>

            <CompactCard title={t("performance_risk_heatmap")}>
              <div className="panel-placeholder">
                <span className="panel-placeholder-icon">🌡</span>
                <span>{t("performance_risk_placeholder")}</span>
              </div>
            </CompactCard>
          </DashboardGrid>

          <CompactCard title={t("performance_engine_analytics")}>
            <AnalyticsSection summary={dashboardData.summary} />
          </CompactCard>
        </SectionContainer>
      )}
    </AsyncPageContent>
  );
}

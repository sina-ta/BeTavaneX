"use client";

import { useCallback } from "react";

import { getReports } from "@/lib/api/reports";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import CreateReportForm from "@/components/forms/CreateReportForm";
import ReportsTable from "@/components/tables/ReportsTable";
import PageHeader from "@/components/ui/PageHeader";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import KPIGrid from "@/components/layout/primitives/KPIGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import { useI18n } from "@/i18n/LanguageProvider";
import type { DailyReport } from "@/types/report";

export default function DailyReportsPage() {
  const { t } = useI18n();
  const fetchReports = useCallback(
    () => getReports(),
    []
  );

  const { status, data, error, reload } =
    useAsyncData<DailyReport[]>(fetchReports);

  return (
    <AsyncPageContent
      status={status}
      data={data}
      error={error}
      loadingTitle={t("daily_reports_title")}
      loadingSubtitle={t("daily_reports_subtitle")}
      loadingMessage="Loading reports..."
      emptyTitle="No reports found"
      onRetry={reload}
    >
      {(reports) => (
        <SectionContainer>
          <PageHeader
            title={t("daily_reports_title")}
            subtitle={t("daily_reports_subtitle")}
            eyebrow={t("eyebrow_field_operations")}
          />

          <DashboardGrid variant="split">
            <CreateReportForm onSuccess={reload} />

            <CompactCard title="Reporting Summary">
              <KPIGrid columns={2}>
                <div className="kpi-card">
                  <div className="kpi-title">Total Reports</div>
                  <div className="kpi-value">{reports.length}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-title">Validation</div>
                  <div className="kpi-value">On</div>
                  <div className="kpi-footer">Trust engine</div>
                </div>
              </KPIGrid>
            </CompactCard>
          </DashboardGrid>

          <CompactCard title="Reports Registry">
            <ReportsTable reports={reports} />
          </CompactCard>
        </SectionContainer>
      )}
    </AsyncPageContent>
  );
}

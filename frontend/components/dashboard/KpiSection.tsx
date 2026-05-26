"use client";

import KpiCard from "@/components/KpiCard";
import KPIGrid from "@/components/layout/primitives/KPIGrid";
import { useI18n } from "@/i18n/LanguageProvider";
import {
  cpiToOperationalHealth,
  ratioToOperationalHealth,
  spiToOperationalHealth,
} from "@/lib/operational/kpiMetrics";
import { formatSeverityLabel } from "@/lib/operational/severity";
import type { DashboardSummary } from "@/types/dashboard";
import type { ProjectKpiTrends } from "@/types/analytics";

type KpiSectionProps = {
  summary: DashboardSummary;
  trends?: ProjectKpiTrends;
};

export default function KpiSection({
  summary,
  trends,
}: KpiSectionProps) {
  const { t } = useI18n();
  const reportingHealth = ratioToOperationalHealth(
    summary.total_reports,
    summary.total_work_orders
  );

  const budgetHealth = cpiToOperationalHealth(
    summary.avg_cpi
  );

  const scheduleHealth = spiToOperationalHealth(
    summary.avg_spi
  );

  return (
    <KPIGrid>
      <KpiCard
        title={t("kpi_work_orders")}
        value={summary.total_work_orders}
        progress={reportingHealth.progress}
        progressSeverity={reportingHealth.severity}
        operationalLabel={`${reportingHealth.progress.toFixed(0)}% ${t("kpi_reported_suffix")}`}
        footer={`${summary.total_reports} ${t("kpi_reports_word")}`}
      />

      <KpiCard
        title={t("kpi_daily_reports")}
        value={summary.total_reports}
        progress={reportingHealth.progress}
        progressSeverity={reportingHealth.severity}
        operationalLabel={t("kpi_coverage")}
        footer={t("kpi_field_reporting")}
      />

      <KpiCard
        title={t("kpi_budget_cpi")}
        value={Number(summary.avg_cpi).toFixed(2)}
        trend={trends?.trends.cpi}
        progress={budgetHealth.progress}
        progressSeverity={budgetHealth.severity}
        operationalLabel={`CPI ${Number(summary.avg_cpi).toFixed(2)}`}
        footer={formatSeverityLabel(budgetHealth.severity)}
      />

      <KpiCard
        title={t("kpi_schedule_spi")}
        value={Number(summary.avg_spi).toFixed(2)}
        trend={trends?.trends.spi}
        progress={scheduleHealth.progress}
        progressSeverity={scheduleHealth.severity}
        operationalLabel={`SPI ${Number(summary.avg_spi).toFixed(2)}`}
        footer={formatSeverityLabel(scheduleHealth.severity)}
      />
    </KPIGrid>
  );
}

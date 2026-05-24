import KpiCard from "@/components/KpiCard";
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
  return (
    <section className="kpi-grid">
      <KpiCard
        title="Total Work Orders"
        value={summary.total_work_orders}
      />

      <KpiCard
        title="Total Reports"
        value={summary.total_reports}
      />

      <KpiCard
        title="Budget Health"
        value={Number(summary.avg_cpi).toFixed(2)}
        trend={trends?.trends.cpi}
        footer="Healthy"
      />

      <KpiCard
        title="Project Speed"
        value={Number(summary.avg_spi).toFixed(2)}
        trend={trends?.trends.spi}
        footer="On Track"
      />
    </section>
  );
}

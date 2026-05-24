import SectionCard from "@/components/ui/SectionCard";
import HealthIndicator from "@/components/ui/HealthIndicator";
import RiskIndicator from "@/components/ui/RiskIndicator";
import type { DashboardSummary } from "@/types/dashboard";

type AnalyticsSectionProps = {
  summary: DashboardSummary;
};

export default function AnalyticsSection({
  summary,
}: AnalyticsSectionProps) {
  const criticalCount = summary.critical_alerts ?? 0;
  const warningCount = summary.warning_alerts ?? 0;

  return (
    <SectionCard title="Project Analytics">
      <section className="grid grid-cols-2 gap-4 text-sm">
        <HealthIndicator
          value={criticalCount}
          status={
            criticalCount > 0 ? "critical" : "healthy"
          }
        />

        <HealthIndicator
          value={warningCount}
          status={
            warningCount > 0 ? "warning" : "stable"
          }
        />

        <RiskIndicator
          risk={
            criticalCount > 0
              ? "critical"
              : warningCount > 0
                ? "warning"
                : "stable"
          }
          compact
        />
      </section>
    </SectionCard>
  );
}

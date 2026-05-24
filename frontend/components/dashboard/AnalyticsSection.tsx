import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
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
    <DashboardGrid variant="analytics">
      <HealthIndicator
        label="Critical Alerts"
        value={criticalCount}
        status={criticalCount > 0 ? "critical" : "healthy"}
      />

      <HealthIndicator
        label="Warnings"
        value={warningCount}
        status={warningCount > 0 ? "warning" : "stable"}
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
    </DashboardGrid>
  );
}

import KPIGrid from "@/components/layout/primitives/KPIGrid";
import HealthIndicator from "@/components/ui/HealthIndicator";
import RiskIndicator from "@/components/ui/RiskIndicator";
import type { WorkforceAnalytics } from "@/types/workforce";
import type { TrendDirection } from "@/lib/operational/severity";

type WorkforceIntelligenceSectionProps = {
  analytics: WorkforceAnalytics;
};

export default function WorkforceIntelligenceSection({
  analytics,
}: WorkforceIntelligenceSectionProps) {
  const overallRisk =
    analytics.available_workers === 0 &&
    analytics.total_workers > 0
      ? "critical"
      : (analytics.avg_productivity_score ?? 0) < 70
        ? "warning"
        : "stable";

  return (
    <section className="dashboard-tasks-section">
      <KPIGrid>
        <HealthIndicator
          label="Total Workers"
          value={analytics.total_workers}
          status="stable"
        />

        <HealthIndicator
          label="Available"
          value={analytics.available_workers}
          status={
            analytics.available_workers > 0
              ? "healthy"
              : "warning"
          }
        />

        <HealthIndicator
          label="Productivity"
          value={analytics.avg_productivity_score ?? "—"}
          status={
            (analytics.avg_productivity_score ?? 0) >= 80
              ? "healthy"
              : "warning"
          }
          trend={analytics.trend as TrendDirection}
        />

        <RiskIndicator risk={overallRisk} />
      </KPIGrid>

      <div className="operational-summary-metrics">
        <div className="operational-summary-item">
          <span className="operational-summary-label">Assigned</span>
          <span className="kpi-value" style={{ fontSize: "var(--font-metric-sm)" }}>
            {analytics.assigned_workers}
          </span>
        </div>
        <div className="operational-summary-item">
          <span className="operational-summary-label">Crews</span>
          <span className="kpi-value" style={{ fontSize: "var(--font-metric-sm)" }}>
            {analytics.crew_count}
          </span>
        </div>
        <div className="operational-summary-item">
          <span className="operational-summary-label">Reliability</span>
          <span className="kpi-value" style={{ fontSize: "var(--font-metric-sm)" }}>
            {analytics.avg_reliability_score ?? "—"}
          </span>
        </div>
      </div>
    </section>
  );
}

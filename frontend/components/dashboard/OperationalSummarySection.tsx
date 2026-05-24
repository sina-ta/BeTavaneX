import CompactCard from "@/components/layout/primitives/CompactCard";
import SeverityBadge from "@/components/ui/SeverityBadge";
import RiskIndicator from "@/components/ui/RiskIndicator";
import { computeOperationalSummary } from "@/lib/operational/dashboardSummary";
import type { DashboardTask } from "@/types/dashboard";

type OperationalSummarySectionProps = {
  tasks: DashboardTask[];
};

export default function OperationalSummarySection({
  tasks,
}: OperationalSummarySectionProps) {
  const summary = computeOperationalSummary(tasks);

  const hasRisks =
    summary.criticalTaskCount > 0 ||
    summary.budgetRiskCount > 0 ||
    summary.scheduleRiskCount > 0;

  if (!hasRisks && tasks.length === 0) {
    return null;
  }

  const overallRisk =
    summary.criticalTaskCount > 0
      ? "critical"
      : summary.budgetRiskCount > 0 ||
          summary.scheduleRiskCount > 0
        ? "warning"
        : "stable";

  return (
    <CompactCard title="Operational Status">
      <section className="operational-summary">
        <section className="operational-summary-metrics">
          <article className="operational-summary-item">
            <span
              className="kpi-value"
              style={{ fontSize: "var(--font-metric-sm)" }}
            >
              {summary.criticalTaskCount}
            </span>
            <span className="operational-summary-label">
              Critical Tasks
            </span>
            <SeverityBadge
              severity={
                summary.criticalTaskCount > 0
                  ? "critical"
                  : "stable"
              }
              label={`${summary.criticalTaskCount} active`}
            />
          </article>

          <article className="operational-summary-item">
            <span
              className="kpi-value"
              style={{ fontSize: "var(--font-metric-sm)" }}
            >
              {summary.budgetRiskCount}
            </span>
            <span className="operational-summary-label">
              Budget Risk
            </span>
            <SeverityBadge
              severity={
                summary.budgetRiskCount > 0
                  ? "over_budget"
                  : "stable"
              }
              label={`${summary.budgetRiskCount} task${summary.budgetRiskCount === 1 ? "" : "s"}`}
            />
          </article>

          <article className="operational-summary-item">
            <span
              className="kpi-value"
              style={{ fontSize: "var(--font-metric-sm)" }}
            >
              {summary.scheduleRiskCount}
            </span>
            <span className="operational-summary-label">
              Schedule Delay
            </span>
            <SeverityBadge
              severity={
                summary.scheduleRiskCount > 0
                  ? "delayed"
                  : "stable"
              }
              label={`${summary.scheduleRiskCount} task${summary.scheduleRiskCount === 1 ? "" : "s"}`}
            />
          </article>
        </section>

        <RiskIndicator risk={overallRisk} />
      </section>
    </CompactCard>
  );
}

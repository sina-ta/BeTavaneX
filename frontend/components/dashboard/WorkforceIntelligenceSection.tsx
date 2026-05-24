import SectionCard from "@/components/ui/SectionCard";
import HealthIndicator from "@/components/ui/HealthIndicator";
import type { WorkforceAnalytics } from "@/types/analytics";

type WorkforceIntelligenceSectionProps = {
  analytics: WorkforceAnalytics;
};

export default function WorkforceIntelligenceSection({
  analytics,
}: WorkforceIntelligenceSectionProps) {
  return (
    <SectionCard title="Workforce Intelligence">
      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <HealthIndicator
          value={analytics.avg_operational_score}
          status={
            analytics.avg_operational_score >= 80
              ? "healthy"
              : "warning"
          }
          trend={analytics.trend}
        />

        <HealthIndicator
          value={`${analytics.avg_attendance_rate}%`}
          status={
            analytics.avg_attendance_rate >= 80
              ? "stable"
              : "delayed"
          }
        />

        <HealthIndicator
          value={analytics.total_workers}
          status="stable"
        />
      </section>
    </SectionCard>
  );
}

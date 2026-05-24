import CostTrendChart from "@/components/charts/CostTrendChart";
import ProductivityChart from "@/components/charts/ProductivityChart";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import type { ProjectKpiTrends } from "@/types/analytics";

type TrendsSectionProps = {
  trends?: ProjectKpiTrends;
};

export default function TrendsSection({
  trends,
}: TrendsSectionProps) {
  if (!trends || trends.points.length === 0) {
    return (
      <p className="text-xs text-[var(--text-muted)]">
        No trend data yet
      </p>
    );
  }

  return (
    <DashboardGrid variant="analytics">
      <CostTrendChart trends={trends} />
      <ProductivityChart trends={trends} />
    </DashboardGrid>
  );
}

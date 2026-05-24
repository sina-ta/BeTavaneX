import KPITrendChart from "./KPITrendChart";
import type { ProjectKpiTrends } from "@/types/analytics";

type CostTrendChartProps = {
  trends: ProjectKpiTrends;
};

export default function CostTrendChart({
  trends,
}: CostTrendChartProps) {
  return (
    <KPITrendChart
      title="Cost Performance Trend"
      metricKey="avg_cpi"
      points={trends.points}
      trend={trends.trends.cpi}
    />
  );
}

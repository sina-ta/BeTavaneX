import KPITrendChart from "./KPITrendChart";
import type { ProjectKpiTrends } from "@/types/analytics";

type ProductivityChartProps = {
  trends: ProjectKpiTrends;
};

export default function ProductivityChart({
  trends,
}: ProductivityChartProps) {
  return (
    <KPITrendChart
      title="Schedule Performance Trend"
      metricKey="avg_spi"
      points={trends.points}
      trend={trends.trends.spi}
    />
  );
}

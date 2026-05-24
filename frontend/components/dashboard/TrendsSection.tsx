import CostTrendChart from "@/components/charts/CostTrendChart";
import ProductivityChart from "@/components/charts/ProductivityChart";
import type { ProjectKpiTrends } from "@/types/analytics";

type TrendsSectionProps = {
  trends?: ProjectKpiTrends;
};

export default function TrendsSection({
  trends,
}: TrendsSectionProps) {
  if (!trends || trends.points.length === 0) {
    return null;
  }

  return (
    <section className="grid grid-cols-1 gap-4 xl:grid-cols-2">
      <CostTrendChart trends={trends} />
      <ProductivityChart trends={trends} />
    </section>
  );
}

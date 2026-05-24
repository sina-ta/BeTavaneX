import AnalyticsCard from "./AnalyticsCard";
import {
  buildSparklinePath,
  extractNumericSeries,
} from "@/lib/charts/sparkline";
import type { KpiTrendPoint } from "@/types/analytics";
import {
  getTrendClass,
  getTrendLabel,
  type TrendDirection,
} from "@/lib/operational/severity";

type KPITrendChartProps = {
  title: string;
  metricKey: "avg_cpi" | "avg_spi" | "cpi" | "spi";
  points: KpiTrendPoint[];
  trend?: TrendDirection;
};

export default function KPITrendChart({
  title,
  metricKey,
  points,
  trend = "stable",
}: KPITrendChartProps) {
  const values = extractNumericSeries(points, metricKey);

  const path = buildSparklinePath(values);

  return (
    <AnalyticsCard
      title={title}
      subtitle={getTrendLabel(trend)}
    >
      {values.length === 0 ? (
        <p className="text-sm opacity-60">
          No trend data yet
        </p>
      ) : (
        <section>
          <svg
            viewBox="0 0 240 64"
            className="h-12 w-full"
            aria-hidden="true"
          >
            <path
              d={path}
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className={getTrendClass(trend)}
            />
          </svg>

          <p
            className={`mt-2 text-sm ${getTrendClass(trend)}`}
          >
            Latest: {values[values.length - 1]}
          </p>
        </section>
      )}
    </AnalyticsCard>
  );
}

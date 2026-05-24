import {
  getTrendClass,
  getTrendLabel,
  type TrendDirection,
} from "@/lib/operational/severity";
import {
  formatSeverityLabel,
  getSeverityClass,
} from "@/lib/operational/severity";

type HealthIndicatorProps = {
  value: string | number;
  status: string;
  trend?: TrendDirection;
};

export default function HealthIndicator({
  value,
  status,
  trend,
}: HealthIndicatorProps) {
  return (
    <section className="flex flex-col gap-1">
      <span className="text-lg font-semibold">{value}</span>

      <span
        className={`badge-base ${getSeverityClass(status)}`}
      >
        {formatSeverityLabel(status)}
      </span>

      {trend && (
        <span className={`text-xs ${getTrendClass(trend)}`}>
          {getTrendLabel(trend)}
        </span>
      )}
    </section>
  );
}

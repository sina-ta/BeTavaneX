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
  label: string;
  value: string | number;
  status: string;
  trend?: TrendDirection;
};

export default function HealthIndicator({
  label,
  value,
  status,
  trend,
}: HealthIndicatorProps) {
  return (
    <section className="kpi-card">
      <span className="kpi-title">{label}</span>
      <span
        className="kpi-value"
        style={{ fontSize: "var(--font-metric-sm)" }}
      >
        {value}
      </span>

      <div className="kpi-card-meta">
        <span className={`badge-base ${getSeverityClass(status)}`}>
          {formatSeverityLabel(status)}
        </span>

        {trend && (
          <span className={`kpi-footer ${getTrendClass(trend)}`}>
            {getTrendLabel(trend)}
          </span>
        )}
      </div>
    </section>
  );
}

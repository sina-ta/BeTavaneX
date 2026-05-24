import ProgressBar from "@/components/ui/ProgressBar";
import SeverityBadge from "@/components/ui/SeverityBadge";
import type { TrendDirection } from "@/lib/operational/severity";
import {
  getTrendClass,
  getTrendLabel,
} from "@/lib/operational/severity";
import type { SeverityLevel } from "@/lib/operational/severity";

type Props = {
  title: string;
  value: string | number;
  footer?: string;
  trend?: TrendDirection;
  progress?: number;
  progressSeverity?: string | SeverityLevel;
  operationalLabel?: string;
};

export default function KpiCard({
  title,
  value,
  footer,
  trend,
  progress,
  progressSeverity,
  operationalLabel,
}: Props) {
  return (
    <section className="kpi-card">
      <section className="kpi-title">{title}</section>

      <section className="kpi-value">{value}</section>

      {progress !== undefined && (
        <section className="kpi-progress">
          <ProgressBar
            value={progress}
            severity={progressSeverity}
            label={operationalLabel}
          />

          {progressSeverity && (
            <SeverityBadge severity={progressSeverity} />
          )}
        </section>
      )}

      {trend && (
        <section
          className={`kpi-footer ${getTrendClass(trend)}`}
        >
          Trend: {getTrendLabel(trend)}
        </section>
      )}

      {footer && !trend && (
        <section className="kpi-footer">{footer}</section>
      )}
    </section>
  );
}

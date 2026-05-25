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
  const showMeta =
    progressSeverity !== undefined || footer || trend;

  return (
    <section className="kpi-card">
      <span className="kpi-title">{title}</span>
      <span className="kpi-value">{value}</span>

      {progress !== undefined && (
        <div className="kpi-progress">
          <ProgressBar
            value={progress}
            severity={progressSeverity}
            label={operationalLabel}
          />
        </div>
      )}

      {showMeta && (
        <div className="kpi-card-meta">
          {progressSeverity !== undefined && (
            <SeverityBadge severity={progressSeverity} />
          )}

          {trend && (
            <span
              className={`kpi-footer ${getTrendClass(trend)}`}
            >
              Trend: {getTrendLabel(trend)}
            </span>
          )}

          {footer && !trend && (
            <span className="kpi-footer">{footer}</span>
          )}
        </div>
      )}
    </section>
  );
}

import {
  resolveSeverity,
  type SeverityLevel,
} from "@/lib/operational/severity";

type ProgressBarProps = {
  value: number;
  severity?: string | SeverityLevel;
  showLabel?: boolean;
  label?: string;
};

const barColorBySeverity: Record<SeverityLevel, string> = {
  stable: "progress-bar-fill--stable",
  good: "progress-bar-fill--good",
  healthy: "progress-bar-fill--healthy",
  warning: "progress-bar-fill--warning",
  over_budget: "progress-bar-fill--over_budget",
  pending: "progress-bar-fill--pending",
  critical: "progress-bar-fill--critical",
  delayed: "progress-bar-fill--delayed",
  default: "progress-bar-fill--default",
};

export default function ProgressBar({
  value,
  severity,
  showLabel = true,
  label,
}: ProgressBarProps) {
  const clamped = Math.min(
    Math.max(value, 0),
    100
  );

  const resolvedSeverity = severity
    ? resolveSeverity(
        typeof severity === "string"
          ? severity
          : severity
      )
    : clamped >= 80
      ? "healthy"
      : clamped >= 50
        ? "warning"
        : "critical";

  const barColor =
    barColorBySeverity[resolvedSeverity];

  return (
    <div className="progress-bar">
      <div className="progress-bar-track">
        <div
          className={`progress-bar-fill ${barColor}`}
          style={{ width: `${clamped}%` }}
        />
      </div>

      {showLabel && (
        <span className="progress-bar-label">
          {label ?? `${clamped.toFixed(1)}%`}
        </span>
      )}
    </div>
  );
}

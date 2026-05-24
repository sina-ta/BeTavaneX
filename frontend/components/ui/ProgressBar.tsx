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

const barColorBySeverity: Record<
  SeverityLevel,
  string
> = {
  stable: "bg-green-500",
  good: "bg-green-500",
  healthy: "bg-green-500",
  warning: "bg-yellow-500",
  over_budget: "bg-yellow-500",
  pending: "bg-yellow-500",
  critical: "bg-red-500",
  delayed: "bg-red-500",
  default: "bg-slate-500",
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

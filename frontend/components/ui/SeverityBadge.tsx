import {
  formatSeverityLabel,
  getSeverityClass,
  resolveSeverity,
  type SeverityLevel,
} from "@/lib/operational/severity";

type SeverityBadgeProps = {
  severity: string | SeverityLevel;
  label?: string;
};

export default function SeverityBadge({
  severity,
  label,
}: SeverityBadgeProps) {
  const resolved =
    typeof severity === "string" &&
    !["stable", "good", "healthy", "warning", "critical", "delayed", "over_budget", "pending", "default"].includes(severity)
      ? resolveSeverity(severity)
      : (severity as SeverityLevel);

  return (
    <span
      className={`badge-base ${getSeverityClass(resolved)}`}
    >
      {label ?? formatSeverityLabel(resolved)}
    </span>
  );
}

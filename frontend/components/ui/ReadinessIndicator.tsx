type ReadinessIndicatorProps = {
  status: string;
  score?: number;
  compact?: boolean;
};

export default function ReadinessIndicator({
  status,
  score,
  compact = false,
}: ReadinessIndicatorProps) {
  const badgeClass =
    status === "ready"
      ? "badge-good"
      : status === "partially_ready"
        ? "badge-warning"
        : status === "blocked" || status === "not_ready"
          ? "badge-critical"
          : "badge-default";

  const label =
    status === "ready"
      ? "Ready"
      : status === "partially_ready"
        ? "Partial"
        : status === "blocked"
          ? "Blocked"
          : "Not Ready";

  return (
    <span
      className={`badge-base ${badgeClass}`}
      title={score !== undefined ? `Readiness: ${score}` : undefined}
    >
      {!compact && "Readiness: "}
      {label}
      {score !== undefined ? ` (${score})` : ""}
    </span>
  );
}

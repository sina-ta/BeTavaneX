type BlockerIndicatorProps = {
  count: number;
  severity?: string;
};

export default function BlockerIndicator({
  count,
  severity = "medium",
}: BlockerIndicatorProps) {
  if (count <= 0) {
    return (
      <span className="badge-base badge-good">
        No blockers
      </span>
    );
  }

  const badgeClass =
    severity === "critical"
      ? "badge-critical"
      : severity === "high"
        ? "badge-warning"
        : "badge-warning";

  return (
    <span className={`badge-base ${badgeClass}`}>
      {count} blocker{count === 1 ? "" : "s"}
    </span>
  );
}

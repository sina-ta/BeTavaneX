type TrustIndicatorProps = {
  trustScore: number;
  status?: string;
  compact?: boolean;
};

export default function TrustIndicator({
  trustScore,
  status,
  compact = false,
}: TrustIndicatorProps) {
  const resolvedStatus =
    status ??
    (trustScore >= 80
      ? "trusted"
      : trustScore >= 60
        ? "warning"
        : "rejected");

  const label =
    resolvedStatus === "trusted"
      ? "Trusted"
      : resolvedStatus === "warning"
        ? "Review"
        : "Low Trust";

  return (
    <span
      className={`badge-base badge-${resolvedStatus === "trusted" ? "good" : resolvedStatus === "warning" ? "warning" : "critical"}`}
      title={`Trust score: ${trustScore}`}
    >
      {!compact && "Trust: "}
      {label} ({trustScore})
    </span>
  );
}

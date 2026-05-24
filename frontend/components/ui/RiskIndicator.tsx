import {
  formatSeverityLabel,
  getSeverityClass,
  resolveSeverity,
} from "@/lib/operational/severity";

type RiskIndicatorProps = {
  risk: string;
  compact?: boolean;
};

export default function RiskIndicator({
  risk,
  compact = false,
}: RiskIndicatorProps) {
  return (
    <div
      className={`
        inline-flex
        items-center
        gap-2
        rounded-full
        px-3
        py-1
        text-sm
        font-medium
        ${getSeverityClass(risk)}
      `}
    >
      {!compact && <span>Risk</span>}
      <span>{formatSeverityLabel(risk)}</span>
    </div>
  );
}

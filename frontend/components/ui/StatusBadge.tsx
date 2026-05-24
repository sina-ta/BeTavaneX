import {
  formatSeverityLabel,
  getSeverityClass,
} from "@/lib/operational/severity";

type StatusBadgeProps = {
  status: string;
  label?: string;
};

export default function StatusBadge({
  status,
  label,
}: StatusBadgeProps) {
  return (
    <span
      className={`badge-base ${getSeverityClass(status)}`}
    >
      {label ?? formatSeverityLabel(status)}
    </span>
  );
}

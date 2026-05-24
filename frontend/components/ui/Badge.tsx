import {
  formatSeverityLabel,
  getSeverityClass,
} from "@/lib/operational/severity";

type BadgeProps = {
  status: string;
};

export default function Badge({ status }: BadgeProps) {
  return (
    <span
      className={`badge-base ${getSeverityClass(status)}`}
    >
      {formatSeverityLabel(status)}
    </span>
  );
}

import type { TrendDirection } from "@/lib/operational/severity";
import { getTrendLabel } from "@/lib/operational/severity";

type Props = {
  title: string;
  value: string | number;
  footer?: string;
  trend?: TrendDirection;
};

export default function KpiCard({
  title,
  value,
  footer,
  trend,
}: Props) {
  return (
    <section className="kpi-card">
      <section className="kpi-title">{title}</section>

      <section className="kpi-value">{value}</section>

      {trend && (
        <section className="kpi-footer">
          Trend: {getTrendLabel(trend)}
        </section>
      )}

      {footer && !trend && (
        <section className="kpi-footer">{footer}</section>
      )}
    </section>
  );
}

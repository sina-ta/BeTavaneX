import type { ReactNode } from "react";

type AnalyticsCardProps = {
  title: string;
  subtitle?: string;
  children: ReactNode;
};

export default function AnalyticsCard({
  title,
  subtitle,
  children,
}: AnalyticsCardProps) {
  return (
    <div className="chart-panel">
      <header className="compact-card__header">
        <h3 className="compact-card__title">{title}</h3>
        {subtitle && (
          <span className="text-xs text-[var(--text-muted)]">
            {subtitle}
          </span>
        )}
      </header>

      <div className="chart-container">{children}</div>
    </div>
  );
}

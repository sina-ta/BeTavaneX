import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
  className?: string;
  columns?: 2 | 3 | 4;
};

export default function KPIGrid({
  children,
  className = "",
  columns = 4,
}: Props) {
  const colClass =
    columns === 2
      ? "kpi-grid--2"
      : columns === 3
        ? "kpi-grid--3"
        : "";

  return (
    <div className={`kpi-grid ${colClass} ${className}`.trim()}>
      {children}
    </div>
  );
}

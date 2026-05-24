import type { ReactNode } from "react";

type Variant = "kpi" | "analytics" | "split" | "stack";

type Props = {
  children: ReactNode;
  variant?: Variant;
  className?: string;
};

const variantClass: Record<Variant, string> = {
  kpi: "dashboard-grid--kpi",
  analytics: "dashboard-grid--analytics",
  split: "dashboard-grid--split",
  stack: "dashboard-grid--stack",
};

export default function DashboardGrid({
  children,
  variant = "stack",
  className = "",
}: Props) {
  return (
    <div
      className={`dashboard-grid ${variantClass[variant]} ${className}`.trim()}
    >
      {children}
    </div>
  );
}

import type { ReactNode } from "react";
import SectionCard from "@/components/ui/SectionCard";

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
    <SectionCard title={title}>
      {subtitle && (
        <p className="mb-4 text-sm opacity-70">
          {subtitle}
        </p>
      )}

      <section className="chart-container min-h-[96px]">
        {children}
      </section>
    </SectionCard>
  );
}

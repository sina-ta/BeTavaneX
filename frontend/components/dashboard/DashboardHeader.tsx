import PageHeader from "@/components/ui/PageHeader";
import type { DashboardData } from "@/types/dashboard";

type DashboardHeaderProps = {
  title?: string;
  subtitle?: string;
};

export default function DashboardHeader({
  title = "Project Overview",
  subtitle = `
    Real-time construction performance
    and project intelligence dashboard
  `,
}: DashboardHeaderProps) {
  return (
    <PageHeader title={title} subtitle={subtitle} />
  );
}

export function DashboardLoadingHeader() {
  return (
    <DashboardHeader
      subtitle="
        Loading dashboard analytics
        and project intelligence...
      "
    />
  );
}

export type { DashboardData };

import type { CommonMessageKey } from "@/i18n/config";

export type NavItem = {
  labelKey: CommonMessageKey;
  href: string;
  icon: string;
  section?: "main" | "operations";
};

type EngineStatusItem = {
  nameKey: CommonMessageKey;
  status: "active";
};

export const mainNavItems: NavItem[] = [
  {
    labelKey: "nav_overview",
    href: "/dashboard/overview",
    icon: "◫",
    section: "main",
  },
  {
    labelKey: "nav_daily_reports",
    href: "/dashboard/daily-reports",
    icon: "📄",
    section: "operations",
  },
  {
    labelKey: "nav_planning",
    href: "/dashboard/planning",
    icon: "▦",
    section: "operations",
  },
  {
    labelKey: "nav_work_orders",
    href: "/dashboard/daily-work-orders",
    icon: "📋",
    section: "operations",
  },
  {
    labelKey: "nav_performance",
    href: "/dashboard/performance",
    icon: "📈",
    section: "operations",
  },
];

export const engineStatusItems: EngineStatusItem[] = [
  { nameKey: "engine_validation", status: "active" as const },
  { nameKey: "engine_lifecycle", status: "active" as const },
  { nameKey: "engine_kpi_analytics", status: "active" as const },
];

export function getPageTitleFromPath(
  pathname: string
): CommonMessageKey {
  const item = mainNavItems.find((nav) => nav.href === pathname);
  if (item) return item.labelKey;
  if (pathname.startsWith("/dashboard/workforce")) {
    return "page_workforce_extension";
  }
  if (pathname.startsWith("/task/")) {
    return "page_task_intelligence";
  }
  return "app_name";
}

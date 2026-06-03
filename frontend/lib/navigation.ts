import type { CommonMessageKey } from "@/i18n/config";
import {
  canAccessOperationalConsole,
  canPlan,
  canSubmitDailyReports,
  getPhase1Role,
} from "@/lib/auth/role-policy";

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

const ALL_NAV_ITEMS: NavItem[] = [
  {
    labelKey: "nav_overview",
    href: "/dashboard/overview",
    icon: "◫",
    section: "main",
  },
  {
    labelKey: "nav_daily_reports",
    href: "/dashboard/console/execution",
    icon: "📄",
    section: "operations",
  },
  {
    labelKey: "nav_planning",
    href: "/dashboard/console",
    icon: "▦",
    section: "operations",
  },
  {
    labelKey: "nav_work_orders",
    href: "/dashboard/console/execution",
    icon: "📋",
    section: "operations",
  },
];

export function getMainNavItemsForRole(): NavItem[] {
  const role = getPhase1Role();
  const items: NavItem[] = [
    {
      labelKey: "nav_overview",
      href: "/dashboard/overview",
      icon: "◫",
      section: "main",
    },
  ];

  if (canAccessOperationalConsole(role)) {
    if (canPlan(role)) {
      items.push({
        labelKey: "nav_planning",
        href: "/dashboard/console",
        icon: "▦",
        section: "operations",
      });
    }
    if (canSubmitDailyReports(role) && !canPlan(role)) {
      items.push({
        labelKey: "nav_field_reports",
        href: "/dashboard/console/execution?focus=report",
        icon: "📄",
        section: "operations",
      });
    } else if (canPlan(role) || canSubmitDailyReports(role)) {
      items.push({
        labelKey: "nav_execution",
        href: "/dashboard/console/execution",
        icon: "⚡",
        section: "operations",
      });
    }
  }

  return items;
}

/** @deprecated Use getMainNavItemsForRole — kept for type compatibility */
export const mainNavItems = ALL_NAV_ITEMS;

export const engineStatusItems: EngineStatusItem[] = [
  { nameKey: "engine_validation", status: "active" as const },
  { nameKey: "engine_lifecycle", status: "active" as const },
  { nameKey: "engine_kpi_analytics", status: "active" as const },
];

export function getPageTitleFromPath(
  pathname: string
): CommonMessageKey {
  const roleItems = getMainNavItemsForRole();
  const item = roleItems.find((nav) => nav.href === pathname);
  if (item) return item.labelKey;
  if (pathname.startsWith("/dashboard/console")) {
    return "nav_planning";
  }
  if (pathname.startsWith("/dashboard/activity-instances")) {
    return "nav_overview";
  }
  return "app_name";
}

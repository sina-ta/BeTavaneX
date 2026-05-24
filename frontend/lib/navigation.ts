export type NavItem = {
  title: string;
  href: string;
  icon: string;
  section?: "main" | "operations";
};

export const mainNavItems: NavItem[] = [
  {
    title: "Overview",
    href: "/dashboard/overview",
    icon: "◫",
    section: "main",
  },
  {
    title: "Daily Reports",
    href: "/dashboard/daily-reports",
    icon: "📄",
    section: "operations",
  },
  {
    title: "Work Orders",
    href: "/dashboard/daily-work-orders",
    icon: "📋",
    section: "operations",
  },
  {
    title: "Workforce",
    href: "/dashboard/workforce",
    icon: "👷",
    section: "operations",
  },
  {
    title: "Performance",
    href: "/dashboard/performance",
    icon: "📈",
    section: "operations",
  },
];

export const engineStatusItems = [
  { name: "Validation Engine", status: "active" as const },
  { name: "Workforce Intelligence", status: "active" as const },
  { name: "Lifecycle Engine", status: "active" as const },
  { name: "KPI Analytics", status: "active" as const },
];

export function getPageTitleFromPath(pathname: string): string {
  const item = mainNavItems.find((nav) => nav.href === pathname);
  if (item) return item.title;
  if (pathname.startsWith("/task/")) return "Task Intelligence";
  return "BetavanX";
}

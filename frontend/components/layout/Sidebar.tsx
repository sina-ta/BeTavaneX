"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import EngineStatusPanel from "@/components/layout/EngineStatusPanel";
import { useI18n } from "@/i18n/LanguageProvider";
import { getMainNavItemsForRole } from "@/lib/navigation";
import { canAccessOperationalConsole } from "@/lib/auth/role-policy";

type Props = {
  collapsed: boolean;
  setCollapsed: (value: boolean) => void;
};

export default function Sidebar({
  collapsed,
  setCollapsed,
}: Props) {
  const pathname = usePathname();
  const { direction, t } = useI18n();

  const navItems = getMainNavItemsForRole();
  const mainItems = navItems.filter((item) => item.section === "main");
  const opsItems = navItems.filter((item) => item.section === "operations");
  const showConsole = canAccessOperationalConsole();

  function renderNavGroup(
    labelKey: Parameters<typeof t>[0],
    items: typeof navItems
  ) {
    return (
      <>
        {!collapsed && (
          <div className="sidebar-section-label">
            {t(labelKey)}
          </div>
        )}

        {items.map((item) => {
          const active =
            pathname === item.href ||
            (item.href !== "/dashboard/overview" &&
              pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className="sidebar-link"
              style={{
                background: active ? "#111c31" : "transparent",
                border: active
                  ? "1px solid #1e293b"
                  : "1px solid transparent",
                justifyContent: collapsed
                  ? "center"
                  : "space-between",
              }}
              title={collapsed ? t(item.labelKey) : undefined}
            >
              <div className="sidebar-link-left">
                <span className="sidebar-nav-icon">{item.icon}</span>
                {!collapsed && <span>{t(item.labelKey)}</span>}
              </div>

              {!collapsed && (
                <span className="sidebar-chevron">
                  {direction === "rtl" ? "‹" : "›"}
                </span>
              )}
            </Link>
          );
        })}
      </>
    );
  }

  return (
    <aside
      className={`
        sidebar-root fixed top-0 left-0 h-screen z-50
        bg-[#081121] border-r border-slate-800
        transition-all duration-300 overflow-hidden
        ${collapsed ? "w-[var(--sidebar-width-collapsed)]" : "w-[var(--sidebar-width)]"}
      `}
    >
      <div className="sidebar-shell">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-4">
            <div className="logo-circle">B</div>

            {!collapsed && (
              <div>
                <div className="logo-text">BetavanX</div>
                <div className="logo-subtitle">
                  {t("brand_subtitle")}
                </div>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => setCollapsed(!collapsed)}
            className="text-slate-400 hover:text-white text-xl"
            aria-label={
              collapsed
                ? t("sidebar_expand")
                : t("sidebar_collapse")
            }
          >
            {collapsed
              ? direction === "rtl"
                ? "‹"
                : "›"
              : direction === "rtl"
                ? "›"
                : "‹"}
          </button>
        </div>

        <nav className="sidebar-menu flex-1">
          {renderNavGroup("nav_command_group", mainItems)}
          {renderNavGroup("nav_operations_group", opsItems)}

          {showConsole && (
            <Link
              href="/dashboard/console"
              className="sidebar-link"
              style={{
                background: pathname.startsWith("/dashboard/console")
                  ? "#111c31"
                  : "transparent",
                border: pathname.startsWith("/dashboard/console")
                  ? "1px solid #1e293b"
                  : "1px solid transparent",
                justifyContent: collapsed ? "center" : "space-between",
              }}
              title={collapsed ? "Operational Console" : undefined}
            >
              <div className="sidebar-link-left">
                <span className="sidebar-nav-icon">▶</span>
                {!collapsed && <span>Operational Console</span>}
              </div>

              {!collapsed && (
                <span className="sidebar-chevron">
                  {direction === "rtl" ? "‹" : "›"}
                </span>
              )}
            </Link>
          )}
        </nav>

        <EngineStatusPanel collapsed={collapsed} />
      </div>
    </aside>
  );
}

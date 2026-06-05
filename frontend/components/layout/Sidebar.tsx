"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import EngineStatusPanel from "@/components/layout/EngineStatusPanel";
import { useI18n } from "@/i18n/LanguageProvider";
import { logout } from "@/lib/auth/auth-client";
import { getMainNavItemsForRole } from "@/lib/navigation";

type Props = {
  collapsed: boolean;
  setCollapsed: (value: boolean) => void;
};

export default function Sidebar({
  collapsed,
  setCollapsed,
}: Props) {
  const pathname = usePathname();
  const router = useRouter();
  const { direction, t } = useI18n();

  const navItems = getMainNavItemsForRole();
  const mainItems = navItems.filter((item) => item.section === "main");
  const opsItems = navItems.filter((item) => item.section === "operations");

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  function renderNavGroup(
    labelKey: Parameters<typeof t>[0],
    items: typeof navItems
  ) {
    return (
      <>
        {!collapsed && (
          <div className="sidebar-section-label">{t(labelKey)}</div>
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
              className={`sidebar-link ${active ? "is-active" : ""}`}
              style={{
                justifyContent: collapsed ? "center" : "space-between",
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
      className={`sidebar-root ${
        collapsed
          ? "w-[var(--sidebar-width-collapsed)]"
          : "w-[var(--sidebar-width)]"
      }`}
    >
      <div className="sidebar-shell">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="logo-circle">B</div>

            {!collapsed && (
              <div className="min-w-0">
                <div className="logo-text">BetavanX</div>
                <div className="logo-subtitle">{t("brand_subtitle")}</div>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => setCollapsed(!collapsed)}
            className="sidebar-toggle"
            aria-label={
              collapsed ? t("sidebar_expand") : t("sidebar_collapse")
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
        </nav>

        <EngineStatusPanel collapsed={collapsed} />

        {!collapsed && (
          <div className="sidebar-footer-actions">
            <button type="button" className="sidebar-link" style={{ width: "100%" }}>
              <div className="sidebar-link-left">
                <span className="sidebar-nav-icon">⚙</span>
                <span>{t("nav_settings")}</span>
              </div>
            </button>
            <button
              type="button"
              className="sidebar-link"
              style={{ width: "100%" }}
              onClick={() => void handleLogout()}
            >
              <div className="sidebar-link-left">
                <span className="sidebar-nav-icon">⎋</span>
                <span>{t("nav_logout")}</span>
              </div>
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}

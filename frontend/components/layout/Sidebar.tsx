"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import EngineStatusPanel from "@/components/layout/EngineStatusPanel";
import { mainNavItems } from "@/lib/navigation";

type Props = {
  collapsed: boolean;
  setCollapsed: (value: boolean) => void;
};

export default function Sidebar({
  collapsed,
  setCollapsed,
}: Props) {
  const pathname = usePathname();

  const mainItems = mainNavItems.filter(
    (item) => item.section === "main"
  );
  const opsItems = mainNavItems.filter(
    (item) => item.section === "operations"
  );

  function renderNavGroup(
    label: string,
    items: typeof mainNavItems
  ) {
    return (
      <>
        {!collapsed && (
          <div className="sidebar-section-label">{label}</div>
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
              title={collapsed ? item.title : undefined}
            >
              <div className="sidebar-link-left">
                <span className="sidebar-nav-icon">{item.icon}</span>
                {!collapsed && <span>{item.title}</span>}
              </div>

              {!collapsed && <span className="sidebar-chevron">›</span>}
            </Link>
          );
        })}
      </>
    );
  }

  return (
    <aside
      className={`
        fixed top-0 left-0 h-screen z-50
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
                  Construction Intelligence
                </div>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => setCollapsed(!collapsed)}
            className="text-slate-400 hover:text-white text-xl"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? "›" : "‹"}
          </button>
        </div>

        <nav className="sidebar-menu flex-1">
          {renderNavGroup("Command", mainItems)}
          {renderNavGroup("Operations", opsItems)}
        </nav>

        <EngineStatusPanel collapsed={collapsed} />
      </div>
    </aside>
  );
}

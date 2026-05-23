"use client";

import Link from "next/link";

import { usePathname } from "next/navigation";

type Props = {
  collapsed: boolean;
  setCollapsed: (
    value: boolean
  ) => void;
};

const menuItems = [

  {
    title: "Overview",
    href: "/dashboard/overview",
    icon: "◫",
  },

  {
    title: "Daily Reports",
    href: "/dashboard/daily-reports",
    icon: "📄",
  },

  {
    title: "Work Orders",
    href: "/dashboard/daily-work-orders",
    icon: "📋",
  },

  {
    title: "Workers",
    href: "/dashboard/workers",
    icon: "👷",
  },

  {
    title: "Performance",
    href: "/dashboard/performance",
    icon: "📈",
  },

];

export default function Sidebar({
  collapsed,
  setCollapsed,
}: Props) {

  const pathname = usePathname();

  return (

    <aside
      className={`
        fixed
        top-0
        left-0
        h-screen
        z-50
        bg-[#081121]
        border-r
        border-slate-800
        transition-all
        duration-300
        overflow-hidden
        ${
          collapsed
            ? "w-[92px]"
            : "w-[280px]"
        }
      `}
    >

      {/* HEADER */}

      <div
        className="
          flex
          items-center
          justify-between
          mb-10
        "
      >

        <div
          className="
            flex
            items-center
            gap-4
          "
        >

          <div className="logo-circle">
            B
          </div>

          {!collapsed && (

            <div>

              <div className="logo-text">
                BetavanX
              </div>

              <div className="logo-subtitle">
                Construction Intelligence
              </div>

            </div>

          )}

        </div>

        <button
          onClick={() =>
            setCollapsed(
              !collapsed
            )
          }
          className="
            text-slate-400
            hover:text-white
            text-xl
          "
        >

          {collapsed ? "›" : "‹"}

        </button>

      </div>

      {/* MENU */}

      <nav className="sidebar-menu">

        {menuItems.map((item) => {

          const active =
            pathname === item.href;

          return (

            <Link
              key={item.href}
              href={item.href}
              className="
                sidebar-link
              "
              style={{

                background: active
                  ? "#111c31"
                  : "transparent",

                border: active
                  ? "1px solid #1e293b"
                  : "1px solid transparent",

                justifyContent:
                  collapsed
                    ? "center"
                    : "space-between",

              }}
            >

              <div
                className="
                  sidebar-link-left
                "
              >

                <span>
                  {item.icon}
                </span>

                {!collapsed && (

                  <span>
                    {item.title}
                  </span>

                )}

              </div>

              {!collapsed && (
                <span>›</span>
              )}

            </Link>

          );
        })}

      </nav>

    </aside>
  );
}
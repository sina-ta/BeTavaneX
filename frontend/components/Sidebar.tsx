"use client";

import Link from "next/link";

const menuItems = [

  {
    title: "Overview",
    href: "/dashboard/overview",
    icon: "📊",
  },

  {
    title: "Work Units",
    href: "/dashboard/work-units",
    icon: "🏗️",
  },

  {
    title: "Daily Reports",
    href: "/dashboard/daily-reports",
    icon: "📝",
  },

  {
    title: "Work Orders",
    href: "/dashboard/daily-work-orders",
    icon: "📋",
  },

  {
    title: "Workers",
    href: "/hr/workers",
    icon: "👷",
  },

  {
    title: "Performance",
    href: "/dashboard/performance",
    icon: "⚡",
  },
];

export default function Sidebar() {

  return (

    <aside className="sidebar">

      <div className="sidebar-logo">

        <div className="logo-circle">

          B

        </div>

        <div>

          <div className="logo-text">

            BetavanX

          </div>

          <div className="logo-subtitle">

            Construction Intelligence

          </div>

        </div>

      </div>

      <nav className="sidebar-menu">

        {menuItems.map((item) => (

          <Link
            key={item.title}
            href={item.href}
            className="sidebar-link"
          >

            <div className="sidebar-link-left">

              <span>

                {item.icon}

              </span>

              <span>

                {item.title}

              </span>

            </div>

          </Link>

        ))}

      </nav>

    </aside>
  );
}
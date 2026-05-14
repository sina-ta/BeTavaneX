"use client";

import { useState } from "react";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {

  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside
        className={`
          fixed left-0 top-0 h-screen bg-black text-white p-6
          transition-all duration-300
          ${collapsed ? "w-20" : "w-64"}
        `}
      >

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="mb-8 text-white text-2xl"
        >
          ☰
        </button>

        <h2
          className={`
            font-bold mb-10 transition-all duration-300 overflow-hidden
            ${collapsed ? "text-center text-2xl" : "text-xl"}
          `}
        >
          {collapsed ? "B" : "BetavanX"}
        </h2>

        <nav className="space-y-4">
          <Link
             href="/dashboard/work-units"
            className="block hover:text-gray-300 text-2xl"
          >
            {collapsed ? "🏗" : "Work Units"}
         </Link>

          <Link 
            href="/dashboard/daily-work-orders"
            className="block hover:text-gray-300 text-2xl"
          >
            {collapsed ? "📋" : "Daily Work Orders"}
          </Link>

          <Link href="/dashboard/daily-reports"
          className="block hover:text-gray-300 text-2xl"
          >
            {collapsed ? "📝" : "Daily Reports"}
          </Link>
          <Link
            href="/dashboard/overview"
            className="block hover:text-gray-300 text-2xl"
          >
            {collapsed ? "📊" : "Overview"}
          </Link>
          
          <Link
            href="/dashboard/workers"
            className="block hover:text-gray-300 text-2xl"
          >
            {collapsed ? "👷" : "Workers"}
          </Link>

          <Link
            href="/dashboard/performance"
            className="block hover:text-gray-300 text-2xl"
          >
            {collapsed ? "⚡" : "Performance"}
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <main
        className={`
          flex-1 p-8 bg-gray-100 min-h-screen
          transition-all duration-300
          ${collapsed ? "ml-20" : "ml-64"}
        `}
      >
        {children}
      </main>
    </div>
  );
}
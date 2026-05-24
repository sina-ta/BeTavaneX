"use client";

import { usePathname } from "next/navigation";

import { getPageTitleFromPath } from "@/lib/navigation";

export default function Topbar() {
  const pathname = usePathname();
  const pageTitle = getPageTitleFromPath(pathname);

  return (
    <header className="topbar">
      <div className="topbar-left">
        <span className="topbar-breadcrumb">
          BetavanX / Command Center
        </span>
        <h1 className="topbar-title">{pageTitle}</h1>
      </div>

      <div className="topbar-center">
        <input
          type="search"
          className="topbar-search"
          placeholder="Search tasks, reports, workforce..."
          aria-label="Search"
        />
      </div>

      <div className="topbar-right">
        <span className="topbar-chip">Project Alpha</span>
        <span className="topbar-chip">Today</span>
        <button
          type="button"
          className="topbar-icon-btn"
          aria-label="Notifications"
        >
          🔔
        </button>
        <div className="topbar-avatar" title="Operator">
          OP
        </div>
      </div>
    </header>
  );
}

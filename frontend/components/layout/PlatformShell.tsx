"use client";

import { useState } from "react";

import Sidebar from "@/components/layout/Sidebar";
import Topbar from "@/components/layout/Topbar";
import { ActiveRoleProvider } from "@/lib/context/ActiveRoleContext";

type Props = {
  children: React.ReactNode;
};

export default function PlatformShell({ children }: Props) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <ActiveRoleProvider>
      <div className="platform-shell">
        <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

        <div
          className={`platform-main ${collapsed ? "is-sidebar-collapsed" : ""}`}
        >
          <Topbar />
          <div className="platform-content">{children}</div>
        </div>
      </div>
    </ActiveRoleProvider>
  );
}

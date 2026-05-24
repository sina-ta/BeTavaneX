"use client";

import { useState } from "react";

import Sidebar from "./Sidebar";

export default function AppShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(true);

  return (
    <div
      className="
        min-h-screen
        bg-[var(--bg-primary)]
        flex
      "
    >
      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
      />

      <main
        className="
          flex-1
          p-4
          md:p-8
          xl:p-10
        "
      >
        {children}
      </main>
    </div>
  );
}

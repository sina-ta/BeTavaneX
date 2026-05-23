"use client";

import { useState } from "react";

import Sidebar from "@/components/layout/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {

  const [collapsed, setCollapsed] =
    useState(true);

  return (

    <div className="bg-[#020617] min-h-screen">

      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
      />

      <main
        className={`
          min-h-screen
          px-10
          py-8
          transition-all
          duration-300
          ${
            collapsed
              ? "ml-[92px]"
              : "ml-[280px]"
          }
        `}
      >

        {children}

      </main>

    </div>
  );
}
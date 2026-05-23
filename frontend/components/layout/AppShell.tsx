"use client";

import Sidebar from "./Sidebar";

export default function AppShell({
  children,
}: {
  children: React.ReactNode;
}) {

  return (

    <div
      className="
        min-h-screen
        bg-[var(--bg-primary)]
        flex
      "
    >

      {/* SIDEBAR */}

      <Sidebar />

      {/* MAIN */}

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
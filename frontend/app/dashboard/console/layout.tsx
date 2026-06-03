"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import {
  canPlan,
  getPhase1Role,
  isReadOnlyInvestor,
} from "@/lib/auth/role-policy";

export default function ConsoleLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const role = getPhase1Role();

  useEffect(() => {
    if (!role) {
      return;
    }
    if (isReadOnlyInvestor(role)) {
      router.replace("/dashboard/overview");
      return;
    }
    if (role === "worker" && !canPlan(role) && pathname === "/dashboard/console") {
      router.replace("/dashboard/console/execution");
    }
  }, [role, pathname, router]);

  if (role && isReadOnlyInvestor(role)) {
    return null;
  }

  return <>{children}</>;
}

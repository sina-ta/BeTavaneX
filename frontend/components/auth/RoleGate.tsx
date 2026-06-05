"use client";

import type { ReactNode } from "react";

import {
  canApproveSteps,
  canAssignWorkOrders,
  canPlan,
  canSubmitDailyReports,
  getPhase1Role,
  isReadOnlyInvestor,
} from "@/lib/auth/role-policy";

type Gate =
  | "plan"
  | "assign"
  | "approve"
  | "report"
  | "read-only-investor";

type Props = {
  allow: Gate;
  children: ReactNode;
  fallback?: ReactNode;
};

const DEFAULT_FALLBACK = (
  <p className="page-subtitle">
    Your role does not have permission for this action.
  </p>
);

function isAllowed(gate: Gate): boolean {
  const role = getPhase1Role();
  switch (gate) {
    case "plan":
      return canPlan(role);
    case "assign":
      return canAssignWorkOrders(role);
    case "approve":
      return canApproveSteps(role);
    case "report":
      return canSubmitDailyReports(role);
    case "read-only-investor":
      return !isReadOnlyInvestor(role);
    default:
      return false;
  }
}

export default function RoleGate({
  allow,
  children,
  fallback = DEFAULT_FALLBACK,
}: Props) {
  if (!isAllowed(allow)) {
    return <>{fallback}</>;
  }
  return <>{children}</>;
}

/**
 * Phase 1 UI role policy — mirrors backend role_policy.py for visibility only.
 * Authorization is always enforced by the API; this module controls UX gates.
 */

import { getAuthRole } from "@/lib/auth/session";
import type { Phase1Role } from "@/lib/api/phase1/types";

export function getPhase1Role(): Phase1Role | null {
  const role = getAuthRole();
  if (
    role === "admin" ||
    role === "supervisor" ||
    role === "worker" ||
    role === "investor"
  ) {
    return role;
  }
  return null;
}

export function canPlan(role: Phase1Role | null = getPhase1Role()): boolean {
  return role === "admin" || role === "supervisor";
}

export function canAssignWorkOrders(
  role: Phase1Role | null = getPhase1Role()
): boolean {
  return role === "admin" || role === "supervisor";
}

export function canApproveSteps(
  role: Phase1Role | null = getPhase1Role()
): boolean {
  return role === "admin" || role === "supervisor";
}

export function canSubmitDailyReports(
  role: Phase1Role | null = getPhase1Role()
): boolean {
  return role === "admin" || role === "supervisor" || role === "worker";
}

export function canReadRuntime(
  role: Phase1Role | null = getPhase1Role()
): boolean {
  return (
    role === "admin" ||
    role === "supervisor" ||
    role === "worker" ||
    role === "investor"
  );
}

export function isReadOnlyInvestor(
  role: Phase1Role | null = getPhase1Role()
): boolean {
  return role === "investor";
}

export function canAccessOperationalConsole(
  role: Phase1Role | null = getPhase1Role()
): boolean {
  return canPlan(role) || canAssignWorkOrders(role) || canSubmitDailyReports(role);
}

export function canViewAdoptionSummary(
  role: Phase1Role | null = getPhase1Role(),
): boolean {
  return role === "admin" || role === "supervisor";
}

/** Stage 28 — project health & attention signals (read-only for investors). */
export function canViewOperationalIntelligence(
  role: Phase1Role | null = getPhase1Role(),
): boolean {
  return canReadRuntime(role);
}

/** Stage 29 — approval queue & supervisor workload detail (not investors). */
export function canViewSupervisorDecisionDetail(
  role: Phase1Role | null = getPhase1Role(),
): boolean {
  return role === "admin" || role === "supervisor";
}

/** Stage 30 — full coordination detail (workers see worker_relevance only). */
export function canViewCoordinationDetail(
  role: Phase1Role | null = getPhase1Role(),
): boolean {
  return role === "admin" || role === "supervisor" || role === "investor";
}

/** Stage 31 — cross-project organizational intelligence (not workers). */
export function canViewOrganizationalIntelligence(
  role: Phase1Role | null = getPhase1Role(),
): boolean {
  return role === "admin" || role === "supervisor" || role === "investor";
}

/** Stage 32 — compressed executive portfolio visibility (admin/investor only). */
export function canViewExecutiveVisibility(
  role: Phase1Role | null = getPhase1Role(),
): boolean {
  return role === "admin" || role === "investor";
}

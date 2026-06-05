import type { Phase1Role } from "@/lib/api/phase1/types";
import type { CommonMessageKey } from "@/i18n/config";

/** Maps Phase 1 roles to human-readable session/mode labels (UI only). */
export const ROLE_MODE_MESSAGE_KEYS: Record<
  Phase1Role,
  CommonMessageKey
> = {
  admin: "role_context_mode_admin",
  supervisor: "role_context_mode_supervisor",
  worker: "role_context_mode_worker",
  investor: "role_context_mode_investor",
};

export const ROLE_TITLE_MESSAGE_KEYS: Record<Phase1Role, CommonMessageKey> = {
  admin: "role_context_title_admin",
  supervisor: "role_context_title_supervisor",
  worker: "role_context_title_worker",
  investor: "role_context_title_investor",
};

export function normalizePhase1Role(
  value: string | null | undefined,
): Phase1Role | null {
  if (
    value === "admin" ||
    value === "supervisor" ||
    value === "worker" ||
    value === "investor"
  ) {
    return value;
  }
  return null;
}

export function initialsFromUsername(username: string | null): string {
  if (!username) {
    return "??";
  }
  const parts = username.trim().split(/[\s._-]+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return username.slice(0, 2).toUpperCase();
}

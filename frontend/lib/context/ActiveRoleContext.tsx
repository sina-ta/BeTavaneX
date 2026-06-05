"use client";

/**
 * UI-only active role context for the top bar.
 * Distinguishes signed-in role from an optional simulated view (local override).
 * No permission changes — display and session clarity only.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";

import {
  normalizePhase1Role,
} from "@/lib/auth/active-role-display";
import { getAuthRole } from "@/lib/auth/session";
import type { Phase1Role } from "@/lib/api/phase1/types";

const ACTIVE_ROLE_OVERRIDE_KEY = "betavanx.active_role_override";

type ActiveRoleContextValue = {
  /** Role from authentication (JWT / login). */
  signedInRole: Phase1Role | null;
  /** Role the UI presents as active (override or signed-in). */
  activeRole: Phase1Role | null;
  isSimulated: boolean;
  hydrated: boolean;
  exitRole: () => void;
  /** Placeholder for future role switch UI — no-op for now. */
  requestRoleSwitch: () => void;
};

const ActiveRoleContext = createContext<ActiveRoleContextValue | null>(null);

function readOverride(): Phase1Role | null {
  if (typeof window === "undefined") {
    return null;
  }
  return normalizePhase1Role(localStorage.getItem(ACTIVE_ROLE_OVERRIDE_KEY));
}

export function ActiveRoleProvider({ children }: { children: ReactNode }) {
  const [signedInRole, setSignedInRole] = useState<Phase1Role | null>(null);
  const [overrideRole, setOverrideRole] = useState<Phase1Role | null>(null);
  const [hydrated, setHydrated] = useState(false);

  const syncFromStorage = useCallback(() => {
    setSignedInRole(normalizePhase1Role(getAuthRole()));
    setOverrideRole(readOverride());
  }, []);

  useEffect(() => {
    syncFromStorage();
    setHydrated(true);

    const onStorage = (event: StorageEvent) => {
      if (
        event.key === ACTIVE_ROLE_OVERRIDE_KEY ||
        event.key === "auth_role" ||
        event.key === null
      ) {
        syncFromStorage();
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [syncFromStorage]);

  const activeRole = overrideRole ?? signedInRole;
  const isSimulated = Boolean(
    overrideRole && signedInRole && overrideRole !== signedInRole,
  );

  const exitRole = useCallback(() => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(ACTIVE_ROLE_OVERRIDE_KEY);
    }
    setOverrideRole(null);
  }, []);

  const requestRoleSwitch = useCallback(() => {
    // Placeholder — role switch picker will plug in here (Stage follow-up).
  }, []);

  const value = useMemo<ActiveRoleContextValue>(
    () => ({
      signedInRole,
      activeRole,
      isSimulated,
      hydrated,
      exitRole,
      requestRoleSwitch,
    }),
    [
      signedInRole,
      activeRole,
      isSimulated,
      hydrated,
      exitRole,
      requestRoleSwitch,
    ],
  );

  return (
    <ActiveRoleContext.Provider value={value}>
      {children}
    </ActiveRoleContext.Provider>
  );
}

export function useActiveRole(): ActiveRoleContextValue {
  const context = useContext(ActiveRoleContext);
  if (context === null) {
    throw new Error("useActiveRole must be used within ActiveRoleProvider");
  }
  return context;
}

/** Dev/demo helper: set a simulated role override (UI testing only). */
export function setActiveRoleOverrideForUi(role: Phase1Role | null): void {
  if (typeof window === "undefined") {
    return;
  }
  if (role === null) {
    localStorage.removeItem(ACTIVE_ROLE_OVERRIDE_KEY);
  } else {
    localStorage.setItem(ACTIVE_ROLE_OVERRIDE_KEY, role);
  }
  window.dispatchEvent(new Event("storage"));
}

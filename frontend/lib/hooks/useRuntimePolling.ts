"use client";

import { useEffect } from "react";

const DEFAULT_INTERVAL_MS = 30_000;

/**
 * Lightweight runtime freshness: periodic reload without new state libraries.
 * WebSockets deferred — polling is sufficient for Phase 1 pilot dashboards.
 */
export function useRuntimePolling(
  reload: () => void,
  enabled: boolean,
  intervalMs: number = DEFAULT_INTERVAL_MS
) {
  useEffect(() => {
    if (!enabled) {
      return;
    }
    const timer = window.setInterval(() => {
      reload();
    }, intervalMs);
    return () => window.clearInterval(timer);
  }, [reload, enabled, intervalMs]);
}

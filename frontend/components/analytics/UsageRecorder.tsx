"use client";

import { useEffect, useRef } from "react";
import { usePathname, useSearchParams } from "next/navigation";

import { recordUsageEvent } from "@/lib/api/phase1/analytics";
import { useProject } from "@/lib/context/ProjectContext";

const SESSION_KEY = "betavanx_pilot_session_id";

function getOrCreateSessionId(): string {
  if (typeof window === "undefined") {
    return "";
  }
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id =
      typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : `sess-${Date.now()}`;
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export default function UsageRecorder() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { selectedProjectId } = useProject();
  const lastPath = useRef<string | null>(null);
  const referrer = useRef<string | null>(null);

  useEffect(() => {
    if (!pathname?.startsWith("/dashboard")) {
      return;
    }

    const query = searchParams.toString();
    const pagePath = query ? `${pathname}?${query}` : pathname;

    if (lastPath.current === pagePath) {
      return;
    }

    const previous = lastPath.current;
    lastPath.current = pagePath;

    void recordUsageEvent({
      event_type: previous === null ? "session_start" : "page_view",
      page_path: pagePath,
      session_id: getOrCreateSessionId(),
      referrer_path: previous ?? referrer.current ?? undefined,
      project_id: selectedProjectId ?? undefined,
    }).catch(() => {
      /* non-blocking pilot analytics */
    });

    referrer.current = pagePath;
  }, [pathname, searchParams, selectedProjectId]);

  return null;
}

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LegacyPlanningRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/dashboard/console");
  }, [router]);
  return null;
}

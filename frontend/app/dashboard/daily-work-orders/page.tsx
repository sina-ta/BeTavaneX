"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LegacyWorkOrdersRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/dashboard/console/execution");
  }, [router]);
  return null;
}

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/dashboard/overview");
  }, [router]);

  return (
    <div className="loading-state">
      <div className="loading-spinner" />
      <span>Redirecting to command center...</span>
    </div>
  );
}

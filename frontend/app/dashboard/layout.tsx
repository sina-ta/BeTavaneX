import { Suspense } from "react";

import UsageRecorder from "@/components/analytics/UsageRecorder";
import PlatformShell from "@/components/layout/PlatformShell";
import { ProjectProvider } from "@/lib/context/ProjectContext";
import { WorkspaceProvider } from "@/lib/context/WorkspaceContext";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProjectProvider>
      <WorkspaceProvider>
        <Suspense fallback={null}>
          <UsageRecorder />
        </Suspense>
        <PlatformShell>{children}</PlatformShell>
      </WorkspaceProvider>
    </ProjectProvider>
  );
}
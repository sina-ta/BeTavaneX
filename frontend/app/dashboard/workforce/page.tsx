"use client";

import { useCallback } from "react";

import {
  getWorkforceWorkers,
  getWorkforceAnalytics,
  WORKFORCE_EXTENSION_ENABLED,
} from "@/modules/workforce";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import PageHeader from "@/components/ui/PageHeader";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import WorkforceTable from "@/components/tables/WorkforceTable";
import WorkforceIntelligenceSection from "@/components/dashboard/WorkforceIntelligenceSection";
import type {
  WorkforceWorker,
  WorkforceAnalytics,
} from "@/modules/workforce";

const PAGE_TITLE = "Workforce Intelligence";
const PAGE_SUBTITLE =
  "Crew readiness, allocation, and field performance";

type WorkforcePageData = {
  workers: WorkforceWorker[];
  analytics: WorkforceAnalytics;
};

export default function WorkforcePage() {
  if (!WORKFORCE_EXTENSION_ENABLED) {
    return (
      <SectionContainer>
        <PageHeader
          title="Workforce Extension"
          subtitle="Workforce is preserved as an optional extension and is not active in the core platform."
          eyebrow="Optional Module"
        />

        <CompactCard title="Extension Disabled">
          <p className="page-subtitle">
            Core operational workflows remain available without
            workforce enabled. Re-enable with{" "}
            <code>
              NEXT_PUBLIC_ENABLE_WORKFORCE_EXTENSION=true
            </code>
            .
          </p>
        </CompactCard>
      </SectionContainer>
    );
  }

  const fetchPageData = useCallback(async () => {
    const [workers, analytics] = await Promise.all([
      getWorkforceWorkers(),
      getWorkforceAnalytics(),
    ]);

    return { workers, analytics };
  }, []);

  const { status, data, error, reload } =
    useAsyncData<WorkforcePageData>(fetchPageData);

  return (
    <AsyncPageContent
      status={status}
      data={data}
      error={error}
      loadingTitle={PAGE_TITLE}
      loadingSubtitle={PAGE_SUBTITLE}
      loadingMessage="Loading workforce intelligence..."
      emptyTitle="No workforce data available"
      onRetry={reload}
    >
      {(pageData) => (
        <SectionContainer>
          <PageHeader
            title={PAGE_TITLE}
            subtitle={PAGE_SUBTITLE}
            eyebrow="Workforce"
          />

          <WorkforceIntelligenceSection
            analytics={pageData.analytics}
          />

          <DashboardGrid variant="split">
            <CompactCard title="Workforce Directory">
              <WorkforceTable workers={pageData.workers} />
            </CompactCard>

            <CompactCard title="Crew Allocation">
              <div className="panel-placeholder">
                <span className="panel-placeholder-icon">👷</span>
                <span>Deployment map — connect GIS overlay</span>
              </div>
            </CompactCard>
          </DashboardGrid>
        </SectionContainer>
      )}
    </AsyncPageContent>
  );
}

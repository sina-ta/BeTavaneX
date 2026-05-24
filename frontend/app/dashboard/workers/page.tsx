"use client";

import { useCallback } from "react";

import { getWorkers, getWorkforceAnalytics } from "@/lib/api/workers";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import PageHeader from "@/components/ui/PageHeader";
import SectionCard from "@/components/ui/SectionCard";
import WorkersTable from "@/components/tables/WorkersTable";
import WorkforceIntelligenceSection from "@/components/dashboard/WorkforceIntelligenceSection";
import type { Worker } from "@/types/worker";
import type { WorkforceAnalytics } from "@/types/analytics";

const PAGE_TITLE = "Workforce Management";
const PAGE_SUBTITLE =
  "Manage active workers, crews and workforce operational performance";

type WorkersPageData = {
  workers: Worker[];
  analytics: WorkforceAnalytics;
};

export default function WorkersPage() {
  const fetchPageData = useCallback(async () => {
    const [workers, analytics] = await Promise.all([
      getWorkers(),
      getWorkforceAnalytics(),
    ]);

    return { workers, analytics };
  }, []);

  const { status, data, error, reload } =
    useAsyncData<WorkersPageData>(fetchPageData);

  return (
    <AsyncPageContent
      status={status}
      data={data}
      error={error}
      loadingTitle={PAGE_TITLE}
      loadingSubtitle={PAGE_SUBTITLE}
      loadingMessage="Loading workers..."
      emptyTitle="No workers found"
      onRetry={reload}
    >
      {(pageData) => (
        <section className="page-wrapper">
          <PageHeader
            title={PAGE_TITLE}
            subtitle={PAGE_SUBTITLE}
          />

          <WorkforceIntelligenceSection
            analytics={pageData.analytics}
          />

          <SectionCard title="Workers Directory">
            <WorkersTable workers={pageData.workers} />
          </SectionCard>
        </section>
      )}
    </AsyncPageContent>
  );
}

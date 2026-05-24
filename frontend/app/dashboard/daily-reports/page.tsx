"use client";

import { useCallback } from "react";

import { getReports } from "@/lib/api/reports";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import CreateReportForm from "@/components/forms/CreateReportForm";
import ReportsTable from "@/components/tables/ReportsTable";
import PageHeader from "@/components/ui/PageHeader";
import SectionCard from "@/components/ui/SectionCard";
import type { DailyReport } from "@/types/report";

const PAGE_TITLE = "Daily Reports";
const PAGE_SUBTITLE =
  "Create, review and monitor daily operational construction reports";

export default function DailyReportsPage() {
  const fetchReports = useCallback(
    () => getReports(),
    []
  );

  const { status, data, error, reload } =
    useAsyncData<DailyReport[]>(fetchReports);

  return (
    <AsyncPageContent
      status={status}
      data={data}
      error={error}
      loadingTitle={PAGE_TITLE}
      loadingSubtitle={PAGE_SUBTITLE}
      loadingMessage="Loading reports..."
      emptyTitle="No reports found"
      onRetry={reload}
    >
      {(reports) => (
        <section className="page-wrapper">
          <PageHeader
            title={PAGE_TITLE}
            subtitle={PAGE_SUBTITLE}
          />

          <CreateReportForm onSuccess={reload} />

          <SectionCard title="Reports List">
            <ReportsTable reports={reports} />
          </SectionCard>
        </section>
      )}
    </AsyncPageContent>
  );
}

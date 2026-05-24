"use client";

import { useCallback } from "react";
import Link from "next/link";

import { getDailyWorkOrders } from "@/lib/api/tasks";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import PageHeader from "@/components/ui/PageHeader";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DenseTableWrapper from "@/components/layout/primitives/DenseTableWrapper";
import KPIGrid from "@/components/layout/primitives/KPIGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import Badge from "@/components/ui/Badge";
import type { WorkOrder } from "@/types/task";

const PAGE_TITLE = "Daily Work Orders";
const PAGE_SUBTITLE = "Active construction work orders and execution";

export default function DailyWorkOrdersPage() {
  const fetchWorkOrders = useCallback(
    () => getDailyWorkOrders(),
    []
  );

  const { status, data, error, reload } =
    useAsyncData<WorkOrder[]>(fetchWorkOrders);

  return (
    <AsyncPageContent
      status={status}
      data={data}
      error={error}
      loadingTitle={PAGE_TITLE}
      loadingSubtitle={PAGE_SUBTITLE}
      loadingMessage="Loading work orders..."
      emptyTitle="No work orders found"
      onRetry={reload}
    >
      {(workOrders) => (
        <SectionContainer>
          <PageHeader
            title={PAGE_TITLE}
            subtitle={PAGE_SUBTITLE}
            eyebrow="Execution"
          />

          <KPIGrid columns={3}>
            <div className="kpi-card">
              <div className="kpi-title">Active</div>
              <div className="kpi-value">{workOrders.length}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-title">High Priority</div>
              <div className="kpi-value">
                {workOrders.filter((o) => o.priority === "high").length}
              </div>
            </div>
            <div className="kpi-card">
              <div className="kpi-title">Lifecycle</div>
              <div className="kpi-value">Live</div>
            </div>
          </KPIGrid>

          <CompactCard title="Active Work Orders">
            <DenseTableWrapper>
              <table className="table-base">
                <thead className="table-head">
                  <tr>
                    <th className="table-head-cell">Task</th>
                    <th className="table-head-cell">Assigned</th>
                    <th className="table-head-cell">Qty</th>
                    <th className="table-head-cell">Unit</th>
                    <th className="table-head-cell">Priority</th>
                    <th className="table-head-cell">Status</th>
                  </tr>
                </thead>

                <tbody>
                  {workOrders.map((item) => (
                    <tr key={item.id} className="table-row">
                      <td className="table-cell">
                        <Link
                          href={`/task/${item.task_id}`}
                          className="text-blue-400 font-medium hover:underline"
                        >
                          {item.task_id}
                        </Link>
                      </td>
                      <td className="table-cell">{item.assigned_to}</td>
                      <td className="table-cell">{item.planned_qty}</td>
                      <td className="table-cell">{item.unit}</td>
                      <td className="table-cell">
                        <Badge status={item.priority} />
                      </td>
                      <td className="table-cell">
                        <Badge status={item.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </DenseTableWrapper>
          </CompactCard>
        </SectionContainer>
      )}
    </AsyncPageContent>
  );
}

"use client";

import { useCallback } from "react";
import Link from "next/link";

import { getDailyWorkOrders } from "@/lib/api/tasks";
import { useAsyncData } from "@/lib/hooks/useAsyncData";
import AsyncPageContent from "@/components/ui/AsyncPageContent";
import PageHeader from "@/components/ui/PageHeader";
import SectionCard from "@/components/ui/SectionCard";
import Badge from "@/components/ui/Badge";
import type { WorkOrder } from "@/types/task";

const PAGE_TITLE = "Daily Work Orders";
const PAGE_SUBTITLE = "Track all active construction tasks";

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
        <div className="page-wrapper">
          <PageHeader
            title={PAGE_TITLE}
            subtitle={PAGE_SUBTITLE}
          />

          <SectionCard title="Active Work Orders">
            <table className="table-base">
              <thead className="table-head">
                <tr>
                  <th className="table-head-cell">Task</th>
                  <th className="table-head-cell">Assigned To</th>
                  <th className="table-head-cell">Planned Qty</th>
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
                        className="
                          text-blue-400
                          font-semibold
                          hover:underline
                        "
                      >
                        {item.task_id}
                      </Link>
                    </td>

                    <td className="table-cell">
                      {item.assigned_to}
                    </td>

                    <td className="table-cell">
                      {item.planned_qty}
                    </td>

                    <td className="table-cell">
                      {item.unit}
                    </td>

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
          </SectionCard>
        </div>
      )}
    </AsyncPageContent>
  );
}

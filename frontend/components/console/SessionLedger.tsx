"use client";

import Link from "next/link";

import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import StatusBadge from "@/components/ui/StatusBadge";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

/**
 * Session ledger of created entities. Because the backend exposes no planning
 * list endpoints, this is the runtime navigation surface for work orders and
 * reports created during the session, and links activities to their runtime view.
 */
export default function SessionLedger() {
  const {
    activityInstances,
    workflowSteps,
    workOrders,
    assignments,
    dailyReports,
    approvals,
  } = useOperational();
  const { selectedProjectId } = useProject();

  const activities = activityInstances.filter(
    (item) => item.project_id === selectedProjectId
  );
  const activityIds = new Set(activities.map((a) => a.id));
  const steps = workflowSteps.filter((step) =>
    activityIds.has(step.activity_instance_id)
  );
  const orders = workOrders.filter(
    (item) => item.project_id === selectedProjectId
  );

  return (
    <CompactCard title="Session Runtime Ledger">
      <DashboardGrid variant="split">
        <div>
          <div className="planning-phase-title">Activity Instances</div>
          <div className="planning-list">
            {activities.length === 0 ? (
              <div className="planning-empty">None yet</div>
            ) : (
              activities.map((activity) => (
                <Link
                  key={activity.id}
                  href={`/dashboard/activity-instances/${activity.id}`}
                  className="planning-list-item"
                >
                  <strong>
                    {activity.code} · {activity.name}
                  </strong>
                  <span className="page-subtitle">
                    Open activity runtime view →
                  </span>
                </Link>
              ))
            )}
          </div>

          <div className="planning-phase-title">Workflow Steps</div>
          <div className="planning-list">
            {steps.length === 0 ? (
              <div className="planning-empty">None yet</div>
            ) : (
              steps.map((step) => (
                <div key={step.id} className="planning-list-item">
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 12,
                    }}
                  >
                    <strong>
                      {step.code} · {step.name}
                    </strong>
                    <StatusBadge status={step.status} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div>
          <div className="planning-phase-title">Work Orders</div>
          <div className="planning-list">
            {orders.length === 0 ? (
              <div className="planning-empty">None yet</div>
            ) : (
              orders.map((order) => (
                <div key={order.id} className="planning-list-item">
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 12,
                    }}
                  >
                    <strong>
                      {order.work_order_number} · {order.title}
                    </strong>
                    <StatusBadge status={order.status} />
                  </div>
                  <span className="page-subtitle">
                    {
                      assignments.filter(
                        (a) => a.work_order_id === order.id
                      ).length
                    }{" "}
                    assignment(s) ·{" "}
                    {
                      dailyReports.filter(
                        (r) => r.work_order_id === order.id
                      ).length
                    }{" "}
                    report(s)
                  </span>
                </div>
              ))
            )}
          </div>

          <div className="planning-phase-title">Daily Reports</div>
          <div className="planning-list">
            {dailyReports.length === 0 ? (
              <div className="planning-empty">None yet</div>
            ) : (
              dailyReports.map((report) => (
                <div key={report.id} className="planning-list-item">
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 12,
                    }}
                  >
                    <strong>{report.report_date}</strong>
                    <StatusBadge status={report.status} />
                  </div>
                  <span className="page-subtitle">
                    {report.reported_manpower ?? 0} manpower ·{" "}
                    {report.reported_equipment ?? 0} equipment
                  </span>
                </div>
              ))
            )}
          </div>

          <div className="planning-phase-title">Approvals</div>
          <div className="planning-list">
            {approvals.length === 0 ? (
              <div className="planning-empty">None yet</div>
            ) : (
              approvals.map((approval) => (
                <div key={approval.id} className="planning-list-item">
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 12,
                    }}
                  >
                    <strong>{approval.approval_type}</strong>
                    <StatusBadge status={approval.status} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </DashboardGrid>
    </CompactCard>
  );
}

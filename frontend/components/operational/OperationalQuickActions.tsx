"use client";

import Link from "next/link";

import {
  canApproveSteps,
  canPlan,
  canSubmitDailyReports,
  getPhase1Role,
  isReadOnlyInvestor,
} from "@/lib/auth/role-policy";
import CompactCard from "@/components/layout/primitives/CompactCard";

export default function OperationalQuickActions() {
  const role = getPhase1Role();

  if (isReadOnlyInvestor(role)) {
    return (
      <CompactCard title="At a glance">
        <p className="page-subtitle">
          Progress and activity list below reflect the latest runtime data.
          Use refresh if numbers look stale.
        </p>
      </CompactCard>
    );
  }

  const actions: { href: string; label: string }[] = [];

  if (canSubmitDailyReports(role)) {
    actions.push({
      href: "/dashboard/console/execution?focus=report",
      label: "Submit daily report",
    });
  }
  if (canApproveSteps(role)) {
    actions.push({
      href: "/dashboard/console/execution?focus=approve",
      label: "Approve workflow step",
    });
  }
  if (canPlan(role)) {
    actions.push({
      href: "/dashboard/console/activity",
      label: "Activities & steps",
    });
    actions.push({
      href: "/dashboard/console/execution?focus=assign",
      label: "Assign work order",
    });
  }

  if (actions.length === 0) {
    return null;
  }

  return (
    <CompactCard title="Do next">
      <p className="page-subtitle" style={{ marginBottom: 8 }}>
        Jump to the most common task for your role on this project.
      </p>
      <div className="operational-quick-actions">
        {actions.map((action) => (
          <Link
            key={action.href}
            href={action.href}
            className="button-primary operational-quick-actions__btn"
          >
            {action.label}
          </Link>
        ))}
      </div>
    </CompactCard>
  );
}

import { resolveSeverity } from "@/lib/operational/severity";
import type { Recommendation } from "@/types/common";
import type { DashboardTask } from "@/types/dashboard";

export type OperationalSummary = {
  criticalTaskCount: number;
  budgetRiskCount: number;
  scheduleRiskCount: number;
  warningTaskCount: number;
};

const severityRank: Record<string, number> = {
  critical: 0,
  delayed: 1,
  over_budget: 2,
  warning: 3,
  pending: 4,
  stable: 5,
  healthy: 6,
  good: 7,
  default: 8,
};

function isBudgetRisk(task: DashboardTask): boolean {
  if (task.cpi < 0.9) {
    return true;
  }

  const factors = task.recommendation?.factors ?? [];
  const text = [
    task.recommendation?.title,
    task.recommendation?.action,
    task.recommendation?.rule_id,
    ...factors,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  return (
    text.includes("budget") ||
    text.includes("cost") ||
    text.includes("cpi")
  );
}

function isScheduleRisk(task: DashboardTask): boolean {
  if (task.spi < 0.9) {
    return true;
  }

  const factors = task.recommendation?.factors ?? [];
  const text = [
    task.recommendation?.title,
    task.recommendation?.action,
    task.recommendation?.rule_id,
    ...factors,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  return (
    text.includes("schedule") ||
    text.includes("delay") ||
    text.includes("spi")
  );
}

export function computeOperationalSummary(
  tasks: DashboardTask[]
): OperationalSummary {
  let criticalTaskCount = 0;
  let budgetRiskCount = 0;
  let scheduleRiskCount = 0;
  let warningTaskCount = 0;

  for (const task of tasks) {
    const alertSeverity = resolveSeverity(task.alert);

    if (alertSeverity === "critical") {
      criticalTaskCount += 1;
    } else if (alertSeverity === "warning") {
      warningTaskCount += 1;
    }

    if (isBudgetRisk(task)) {
      budgetRiskCount += 1;
    }

    if (isScheduleRisk(task)) {
      scheduleRiskCount += 1;
    }
  }

  return {
    criticalTaskCount,
    budgetRiskCount,
    scheduleRiskCount,
    warningTaskCount,
  };
}

export function getPrimaryRecommendation(
  tasks: DashboardTask[]
): Recommendation | undefined {
  const withRecommendation = tasks.filter(
    (task) => task.recommendation
  );

  if (withRecommendation.length === 0) {
    return undefined;
  }

  return [...withRecommendation].sort((a, b) => {
    const aSeverity =
      severityRank[
        resolveSeverity(
          a.recommendation?.severity ??
            a.alert
        )
      ] ?? 8;

    const bSeverity =
      severityRank[
        resolveSeverity(
          b.recommendation?.severity ??
            b.alert
        )
      ] ?? 8;

    return aSeverity - bSeverity;
  })[0].recommendation;
}

export type SeverityLevel =
  | "stable"
  | "good"
  | "healthy"
  | "warning"
  | "critical"
  | "delayed"
  | "over_budget"
  | "pending"
  | "default";

export type TrendDirection =
  | "improving"
  | "declining"
  | "stable";

export const severityClassMap: Record<
  SeverityLevel,
  string
> = {
  stable: "badge-good",
  good: "badge-good",
  healthy: "badge-good",
  warning: "badge-warning",
  critical: "badge-critical",
  delayed: "badge-critical",
  over_budget: "badge-warning",
  pending: "badge-warning",
  default: "badge-default",
};

export const severityLabelMap: Record<
  SeverityLevel,
  string
> = {
  stable: "Stable",
  good: "Good",
  healthy: "Healthy",
  warning: "Warning",
  critical: "Critical",
  delayed: "Delayed",
  over_budget: "Over Budget",
  pending: "Pending",
  default: "Unknown",
};

const severityMatchers: Array<{
  test: (value: string) => boolean;
  level: SeverityLevel;
}> = [
  {
    test: (value) =>
      value.includes("critical") || value.includes("🔴"),
    level: "critical",
  },
  {
    test: (value) =>
      value.includes("warning") || value.includes("🟡"),
    level: "warning",
  },
  {
    test: (value) =>
      value.includes("delayed") || value.includes("delay"),
    level: "delayed",
  },
  {
    test: (value) =>
      value.includes("over budget") ||
      value.includes("over_budget") ||
      value.includes("cost overrun"),
    level: "over_budget",
  },
  {
    test: (value) =>
      value.includes("stable") || value.includes("🟢"),
    level: "stable",
  },
  {
    test: (value) =>
      value.includes("healthy") || value.includes("good"),
    level: "healthy",
  },
  {
    test: (value) => value.includes("approved"),
    level: "good",
  },
  {
    test: (value) => value.includes("pending"),
    level: "pending",
  },
];

export function resolveSeverity(
  input: string
): SeverityLevel {
  const normalized = input.toLowerCase().trim();

  for (const matcher of severityMatchers) {
    if (matcher.test(normalized)) {
      return matcher.level;
    }
  }

  return "default";
}

export function getSeverityClass(
  input: string
): string {
  return severityClassMap[resolveSeverity(input)];
}

export function formatSeverityLabel(
  input: string
): string {
  const level = resolveSeverity(input);

  if (level !== "default") {
    return severityLabelMap[level];
  }

  return input;
}

export function getTrendLabel(
  trend: TrendDirection
): string {
  switch (trend) {
    case "improving":
      return "Improving";
    case "declining":
      return "Declining";
    default:
      return "Stable";
  }
}

export function getTrendClass(
  trend: TrendDirection
): string {
  switch (trend) {
    case "improving":
      return "text-green-400";
    case "declining":
      return "text-red-400";
    default:
      return "text-slate-400";
  }
}

import { apiRequest } from "@/lib/api/client";

export type UsageEventType = "page_view" | "session_start";

export interface UsageEventPayload {
  event_type?: UsageEventType;
  page_path: string;
  session_id?: string;
  referrer_path?: string;
  project_id?: string;
}

export interface AdoptionSummary {
  generated_at: string;
  usage: {
    event_count: number;
    distinct_users: number;
    distinct_users_usage_only: number;
    by_role_events: Record<string, number>;
    page_views: Record<string, number>;
    least_used_dashboard_paths: string[];
    event_types: Record<string, number>;
    navigation_backtrack_sessions: number;
  };
  mutations: {
    audit_record_count: number;
    by_action: Record<string, number>;
    by_role: Record<string, number>;
    daily_report_actions: number;
    approval_actions: number;
    assign_actions: number;
  };
  retention: {
    user_active_days: { username: string; active_days: number; dates: string[] }[];
    users_with_multi_day_activity: number;
  };
  db_snapshot: Record<string, number>;
  bottleneck_hints: string[];
}

export async function recordUsageEvent(
  payload: UsageEventPayload,
): Promise<{ status: string; recorded_at: string }> {
  return apiRequest("/analytics/usage-events", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getAdoptionSummary(): Promise<AdoptionSummary> {
  return apiRequest<AdoptionSummary>("/analytics/adoption-summary");
}

export type MaturityBand =
  | "ESTABLISHED"
  | "DEVELOPING"
  | "EMERGING"
  | "STRAINED"
  | "UNKNOWN";

export type CapacityBand = "BALANCED" | "PRESSURED" | "SATURATED" | "UNKNOWN";

export interface OrganizationalSignal {
  signal_type: string;
  severity: "info" | "warning" | "critical";
  message: string;
  evidence: string;
  count: number;
}

export interface OrganizationalIntelligence {
  generated_at: string;
  data_available: boolean;
  projects_analyzed: number;
  maturity_band: MaturityBand;
  maturity_score: number | null;
  maturity_summary: string;
  maturity_components: {
    factor: string;
    score: number;
    detail: string;
  }[];
  capacity_band: CapacityBand;
  capacity_summary: string;
  cross_project_findings: OrganizationalSignal[];
  organizational_bottlenecks: OrganizationalSignal[];
  supervisor_trends: {
    username: string;
    role: string;
    approvals_7d: number;
    assignments_7d: number;
    audit_actions_7d: number;
    observation: string;
    concentration_risk: boolean;
  }[];
  culture_indicators: OrganizationalSignal[];
  multi_project_coordination: OrganizationalSignal[];
  project_snapshots: {
    project_id: string;
    project_code: string;
    project_name: string;
    health_band: string;
    coordination_pressure: string;
    open_blockers: number;
    pending_approvals: number;
    reports_last_7_days: number;
    stalled_steps: number;
  }[];
  organizational_attention: string[];
  false_positive_notes: string[];
}

export async function getOrganizationalIntelligence(): Promise<OrganizationalIntelligence> {
  return apiRequest<OrganizationalIntelligence>(
    "/analytics/organizational-intelligence",
  );
}

export type PortfolioBand = "HEALTHY" | "STABLE" | "CAUTION" | "CRITICAL" | "UNKNOWN";

export interface ExecutiveVisibility {
  generated_at: string;
  data_available: boolean;
  executive_summary: string;
  portfolio_health: {
    overall_band: PortfolioBand;
    summary: string;
    projects_analyzed: number;
    health_distribution: Record<string, number>;
    coordination_pressure_distribution: Record<string, number>;
    maturity_band: MaturityBand;
    capacity_band: CapacityBand;
    deteriorating_project_codes: string[];
    stable_project_codes: string[];
  };
  strategic_risks: OrganizationalSignal[];
  trend_narratives: {
    narrative_id: string;
    trend_direction: "improving" | "stable" | "worsening" | "unknown";
    message: string;
    evidence: string;
  }[];
  leadership_priorities: {
    rank: number;
    concern: string;
    attention_level: "immediate" | "planned" | "monitor" | "stable";
    evidence: string;
    suggested_focus: string;
  }[];
  pressure_indicators: {
    indicator_type: string;
    severity: "info" | "warning" | "critical";
    message: string;
    evidence: string;
  }[];
  strategic_attention: string[];
  false_positive_notes: string[];
}

export async function getExecutiveVisibility(): Promise<ExecutiveVisibility> {
  return apiRequest<ExecutiveVisibility>("/analytics/executive-visibility");
}

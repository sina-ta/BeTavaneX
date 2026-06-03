import { apiRequest } from "@/lib/api/client";

export type HealthBand = "GOOD" | "ATTENTION" | "AT_RISK" | "UNKNOWN";

export interface OperationalRecommendation {
  severity: "info" | "warning" | "critical";
  message: string;
  rationale: string;
}

export interface PriorityItem {
  rank: number;
  category: string;
  priority_score: number;
  severity: "info" | "warning" | "critical";
  title: string;
  explanation: string;
  resource_type?: string;
  resource_id?: string;
  workflow_step_id?: string | null;
  suggested_action: string;
}

export interface ApprovalQueueItem {
  queue_position: number;
  approval_id: string;
  workflow_step_id: string;
  step_code: string;
  activity_code: string;
  approval_type: string;
  status: string;
  days_pending: number;
  overdue: boolean;
  priority_score: number;
  explanation: string;
  suggested_action: string;
}

export interface WorkloadImbalance {
  imbalance_type: string;
  severity: "info" | "warning" | "critical";
  message: string;
  evidence: string;
  metric: number;
}

export interface OperationalDecisionSupport {
  project_id: string;
  generated_at: string;
  data_available: boolean;
  priority_queue: PriorityItem[];
  supervisor_guidance: string[];
  approval_queue: ApprovalQueueItem[];
  blocker_guidance: OperationalSignal[];
  workload_imbalance: WorkloadImbalance[];
  recommendations: OperationalRecommendation[];
  false_positive_notes: string[];
}

export interface OperationalIntelligence {
  project_id: string;
  generated_at: string;
  data_available: boolean;
  stall_threshold_days: number;
  approval_delay_threshold_days: number;
  health: {
    score: number | null;
    band: HealthBand;
    components: { factor: string; impact: number; detail: string }[];
    summary: string;
  };
  stagnation: OperationalSignal[];
  approval_delays: OperationalSignal[];
  blocker_trends: OperationalSignal[];
  anomalies: OperationalSignal[];
  attention_needed: AttentionItem[];
  predictions: PredictiveSignal[];
  false_positive_notes: string[];
  decision_support?: OperationalDecisionSupport | null;
  coordination_intelligence?: OperationalCoordinationIntelligence | null;
}

export type CoordinationBand = "ALIGNED" | "FRAGMENTED" | "STRESSED" | "UNKNOWN";

export interface CrossRoleDependency {
  from_role: string;
  to_role: string;
  dependency_type: string;
  severity: "info" | "warning" | "critical";
  message: string;
  evidence: string;
}

export interface HandoffRisk {
  handoff_type: string;
  severity: "info" | "warning" | "critical";
  message: string;
  workflow_step_id?: string | null;
  context: string;
}

export interface TeamExecutionFlow {
  reports_last_7_days: number;
  approvals_last_7_days: number;
  assignments_last_7_days: number;
  open_coordination_dependencies: number;
  coordination_density: number;
  supervisor_responsiveness_ratio: number;
  workflow_step_count: number;
  activity_count: number;
}

export interface CoordinationAttention {
  severity: "info" | "warning" | "critical";
  category: string;
  message: string;
  workflow_step_id?: string | null;
}

export interface OperationalCoordinationIntelligence {
  project_id: string;
  generated_at: string;
  data_available: boolean;
  coordination_band: CoordinationBand;
  coordination_score: number | null;
  coordination_summary: string;
  bottlenecks: OperationalSignal[];
  cross_role_dependencies: CrossRoleDependency[];
  synchronization: OperationalSignal[];
  handoff_risks: HandoffRisk[];
  communication_gaps: OperationalSignal[];
  team_execution_flow: TeamExecutionFlow;
  coordination_attention: CoordinationAttention[];
  worker_relevance: string[];
  false_positive_notes: string[];
}

export interface OperationalSignal {
  signal_type: string;
  severity: "info" | "warning" | "critical";
  message: string;
  evidence: string;
  count: number;
}

export interface AttentionItem {
  severity: "info" | "warning" | "critical";
  category: string;
  message: string;
  resource_type?: string;
  resource_id?: string;
  workflow_step_id?: string;
}

export interface PredictiveSignal {
  forecast: string;
  confidence: "low" | "medium" | "high";
  reason: string;
  workflow_step_id?: string | null;
}

export async function getProjectOperationalIntelligence(
  projectId: string,
): Promise<OperationalIntelligence> {
  return apiRequest(
    `/analytics/projects/${projectId}/operational-intelligence`,
  );
}

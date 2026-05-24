export interface LifecycleBlocker {
  id: number;
  blocker_type: string;
  severity: string;
  title: string;
  description?: string | null;
  operational_impact?: string | null;
  expected_delay_days?: number | null;
  responsible_entity?: string | null;
  resolution_state: string;
}

export interface LifecycleDependency {
  id: number;
  dependency_type: string;
  depends_on_entity_type?: string | null;
  depends_on_entity_id?: number | null;
  is_satisfied: boolean;
  description?: string | null;
}

export interface LifecycleApproval {
  id: number;
  level: number;
  required_role: string;
  status: string;
}

export interface LifecycleEscalation {
  id: number;
  trigger_type: string;
  escalation_level: string;
  severity: string;
  resolution_state: string;
}

export interface TaskLifecycleState {
  task_id: number;
  work_order_id: number;
  task_state: string;
  work_order_state: string;
  maturity_level?: string | null;
  responsible_entity?: string | null;
  blockers: LifecycleBlocker[];
  dependencies: LifecycleDependency[];
  approvals: LifecycleApproval[];
  escalations: LifecycleEscalation[];
  readiness?: {
    status: string;
    score: number;
  } | null;
}

export interface ExecutionReadiness {
  task_id: number;
  status: string;
  score: number;
  can_start: boolean;
  factors: Array<{
    factor: string;
    passed: boolean;
    message: string;
    severity?: string;
  }>;
}

export interface TimelineEvent {
  id: number;
  event_type: string;
  title: string;
  description?: string | null;
  severity?: string | null;
  occurred_at: string;
  payload: Record<string, unknown>;
}

export interface LifecycleSummary {
  total_tasks_tracked: number;
  total_work_orders_tracked: number;
  task_state_distribution: Record<string, number>;
  open_blockers: number;
  open_escalations: number;
}

export interface WorkerScores {
  productivity?: number | null;
  reliability?: number | null;
  quality?: number | null;
  safety?: number | null;
  teamwork?: number | null;
  discipline?: number | null;
  leadership?: number | null;
}

export interface WorkforceWorker {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  trade: string;
  current_role?: string | null;
  crew?: string | null;
  skill_level?: string | null;
  availability_status: string;
  daily_cost?: number | null;
  scores: WorkerScores;
  assignment_readiness: string;
  operational_score?: number | null;
  is_active: boolean;
}

export interface WorkforceWorkerDetail extends WorkforceWorker {
  phone?: string | null;
  current_project_id?: number | null;
  safety_clearance?: string | null;
  skills: string[];
  certifications: string[];
}

export interface WorkforceCrew {
  id: number;
  name: string;
  trade?: string | null;
  supervisor?: string | null;
  active_project_id?: number | null;
  performance_score?: number | null;
  utilization_rate?: number | null;
  worker_count: number;
}

export interface EligibilityFactor {
  factor: string;
  passed: boolean;
  message: string;
}

export interface EligibilitySummary {
  worker_id: number;
  task_id?: number | null;
  eligible: boolean;
  factors: EligibilityFactor[];
}

export interface OperationalSignal {
  signal: string;
  severity: string;
  message: string;
}

export interface DailyReportContribution {
  report_count: number;
  total_actual_qty: number;
  total_manpower_logged: number;
  delay_events: number;
  linked_task_ids?: number[];
  source: string;
}

export interface WorkerIntelligence {
  worker_id: number;
  full_name: string;
  trade: string;
  crew?: string | null;
  availability_status: string;
  scores: WorkerScores;
  operational_signals: OperationalSignal[];
  daily_report_contribution: DailyReportContribution;
  assignment_count: number;
  attendance_rate?: number;
  eligibility_summary: EligibilitySummary;
}

export interface WorkforceAnalytics {
  total_workers: number;
  available_workers: number;
  assigned_workers: number;
  avg_productivity_score?: number | null;
  avg_reliability_score?: number | null;
  crew_count: number;
  trend: string;
  workers: WorkerIntelligence[];
}

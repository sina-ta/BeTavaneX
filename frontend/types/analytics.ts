import type { TrendDirection } from "@/lib/operational/severity";

export interface KpiTrendPoint {
  recorded_at: string;
  avg_cpi?: number;
  avg_spi?: number;
  cpi?: number;
  spi?: number;
  progress_percent?: number;
  final_score?: number;
  risk_score?: number;
}

export interface TrendSummary {
  cpi: TrendDirection;
  spi: TrendDirection;
  progress?: TrendDirection;
}

export interface ProjectKpiTrends {
  points: KpiTrendPoint[];
  trends: TrendSummary;
}

export interface TaskKpiTrends {
  task_id: number;
  points: KpiTrendPoint[];
  trends: TrendSummary;
}

export interface WorkforceAnalytics {
  total_workers: number;
  avg_operational_score: number;
  avg_attendance_rate: number;
  trend: TrendDirection;
  workers: WorkerIntelligence[];
}

export interface WorkerIntelligence {
  worker_id: number;
  full_name: string;
  role: string;
  crew: string;
  attendance_rate: number;
  productivity_score: number;
  crew_efficiency: number;
  operational_score: number;
  skill_performance: {
    productivity: number;
    quality: number;
    safety: number;
    discipline: number;
  };
  assignment_count: number;
  factors: Array<{
    factor: string;
    status: string;
    message: string;
  }>;
}

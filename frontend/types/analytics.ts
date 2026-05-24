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

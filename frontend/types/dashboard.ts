import type { Recommendation } from "./common";
import type { ProjectKpiTrends } from "./analytics";
import type { ValidationSummary } from "./validation";

export interface DashboardSummary {
  total_work_orders: number;
  total_reports: number;
  avg_cpi: number;
  avg_spi: number;
  critical_alerts?: number;
  warning_alerts?: number;
}

export interface DashboardTask {
  task_id: number;
  progress_percent: number;
  cpi: number;
  spi: number;
  alert: string;
  recommendation?: Recommendation;
}

export interface DashboardData {
  summary: DashboardSummary;
  tasks: DashboardTask[];
  trends?: ProjectKpiTrends;
  validation_summary?: ValidationSummary;
}

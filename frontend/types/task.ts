import type { Recommendation } from "./common";
import type { DailyReport } from "./report";

export interface WorkOrder {
  id: number;
  project_id: number;
  task_id: number;
  assigned_to: string;
  planned_qty: number;
  unit: string;
  priority: string;
  status: string;
  created_by: string;
}

export interface TaskDetail {
  task_id: number;
  assigned_to: string;
  planned_qty: number;
  status: string;
  cpi: number;
  spi: number;
  progress_percent: number;
  alert: string;
  recommendation: Recommendation;
  reports: DailyReport[];
}

export interface TaskDetailError {
  error: string;
}

import { apiRequest } from "./client";
import type {
  KpiTrendPoint,
  ProjectKpiTrends,
  TaskKpiTrends,
} from "@/types/analytics";

export function getProjectKpiTrends(): Promise<ProjectKpiTrends> {
  return apiRequest<ProjectKpiTrends>(
    "/analytics/kpi-trends"
  );
}

export function getTaskKpiTrends(
  taskId: number
): Promise<TaskKpiTrends> {
  return apiRequest<TaskKpiTrends>(
    `/analytics/kpi-trends/${taskId}`
  );
}

export type { KpiTrendPoint };

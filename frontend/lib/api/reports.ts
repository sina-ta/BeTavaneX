import { apiRequest } from "./client";
import type {
  CreateReportPayload,
  CreateReportResponse,
  DailyReport,
} from "@/types/report";

export function getReports(): Promise<DailyReport[]> {
  return apiRequest<DailyReport[]>("/daily-reports");
}

export function createReport(
  payload: CreateReportPayload
): Promise<CreateReportResponse> {
  return apiRequest<CreateReportResponse>(
    "/daily-report",
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

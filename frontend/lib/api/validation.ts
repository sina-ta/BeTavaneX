import { apiRequest } from "./client";
import type {
  ValidationPipelineResult,
  ValidationSummary,
  OperationalAnomaly,
  ReportValidation,
} from "@/types/validation";
import type { CreateReportPayload } from "@/types/report";

export function getValidationSummary(): Promise<ValidationSummary> {
  return apiRequest<ValidationSummary>("/validation/summary");
}

export function getActiveAnomalies(): Promise<OperationalAnomaly[]> {
  return apiRequest<OperationalAnomaly[]>("/validation/anomalies");
}

export function getReportValidation(
  reportId: number
): Promise<ReportValidation> {
  return apiRequest<ReportValidation>(
    `/validation/reports/${reportId}`
  );
}

export function previewReportValidation(
  payload: CreateReportPayload
): Promise<ValidationPipelineResult> {
  return apiRequest<ValidationPipelineResult>(
    "/validation/reports/preview",
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

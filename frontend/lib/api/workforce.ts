import { apiRequest } from "./client";
import type {
  WorkforceWorker,
  WorkforceWorkerDetail,
  WorkforceAnalytics,
  WorkerIntelligence,
  WorkforceCrew,
  EligibilitySummary,
} from "@/types/workforce";

export function getWorkforceWorkers(): Promise<WorkforceWorker[]> {
  return apiRequest<WorkforceWorker[]>("/workforce/workers");
}

export function getWorkforceWorkerById(
  id: number
): Promise<WorkforceWorkerDetail> {
  return apiRequest<WorkforceWorkerDetail>(
    `/workforce/workers/${id}`
  );
}

export function getWorkerIntelligence(
  id: number
): Promise<WorkerIntelligence> {
  return apiRequest<WorkerIntelligence>(
    `/workforce/workers/${id}/intelligence`
  );
}

export function getWorkforceAnalytics(): Promise<WorkforceAnalytics> {
  return apiRequest<WorkforceAnalytics>(
    "/workforce/workers/analytics"
  );
}

export function getWorkforceCrews(): Promise<WorkforceCrew[]> {
  return apiRequest<WorkforceCrew[]>("/workforce/crews");
}

export function getWorkerEligibility(
  workerId: number,
  taskId?: number
): Promise<EligibilitySummary> {
  const query = taskId ? `?task_id=${taskId}` : "";
  return apiRequest<EligibilitySummary>(
    `/workforce/workers/${workerId}/eligibility${query}`
  );
}

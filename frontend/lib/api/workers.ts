import { apiRequest } from "./client";
import type { Worker } from "@/types/worker";
import type {
  WorkerIntelligence,
  WorkforceAnalytics,
} from "@/types/analytics";

export function getWorkers(): Promise<Worker[]> {
  return apiRequest<Worker[]>("/workers");
}

export function getWorkerById(
  id: number
): Promise<WorkerIntelligence> {
  return apiRequest<WorkerIntelligence>(
    `/workers/${id}/intelligence`
  );
}

export function getWorkforceAnalytics(): Promise<WorkforceAnalytics> {
  return apiRequest<WorkforceAnalytics>(
    "/workers/analytics"
  );
}

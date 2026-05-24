import { apiRequest } from "./client";
import type {
  TaskLifecycleState,
  ExecutionReadiness,
  TimelineEvent,
  LifecycleSummary,
  LifecycleBlocker,
} from "@/types/lifecycle";

export function getLifecycleSummary(): Promise<LifecycleSummary> {
  return apiRequest<LifecycleSummary>("/lifecycle/summary");
}

export function getTaskLifecycle(
  taskId: number
): Promise<TaskLifecycleState> {
  return apiRequest<TaskLifecycleState>(
    `/lifecycle/tasks/${taskId}`
  );
}

export function transitionTaskState(
  taskId: number,
  payload: {
    to_state: string;
    triggered_by?: string;
    reason?: string;
  }
): Promise<Record<string, unknown>> {
  return apiRequest(`/lifecycle/tasks/${taskId}/transition`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getTaskReadiness(
  taskId: number
): Promise<ExecutionReadiness> {
  return apiRequest<ExecutionReadiness>(
    `/lifecycle/tasks/${taskId}/readiness`
  );
}

export function getTaskTimeline(
  taskId: number
): Promise<TimelineEvent[]> {
  return apiRequest<TimelineEvent[]>(
    `/lifecycle/tasks/${taskId}/timeline`
  );
}

export function createOperationalBlocker(
  payload: Omit<LifecycleBlocker, "id" | "resolution_state"> & {
    entity_type: string;
    entity_id: number;
    task_id?: number;
    work_order_id?: number;
  }
): Promise<LifecycleBlocker> {
  return apiRequest<LifecycleBlocker>("/lifecycle/blockers", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

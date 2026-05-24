import { apiRequest } from "./client";
import type {
  TaskDetail,
  WorkOrder,
} from "@/types/task";

export function getDailyWorkOrders(): Promise<WorkOrder[]> {
  return apiRequest<WorkOrder[]>("/daily-work-orders");
}

export function getTaskById(
  taskId: number
): Promise<TaskDetail> {
  return apiRequest<TaskDetail>(`/task/${taskId}`);
}

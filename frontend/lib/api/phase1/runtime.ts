/**
 * Phase 1 runtime API — typed wrappers over the `/runtime/*` endpoints.
 */

import { apiRequest } from "@/lib/api/client";
import type {
  ActivityInstance,
  ActivityInstanceListParams,
  ActivityInstanceRuntimeView,
  Approval,
  DailyReport,
  DailyReportCreate,
  DailyReportListParams,
  PaginatedResponse,
  Project,
  ProjectDashboard,
  ProjectDashboardSummary,
  ProjectListParams,
  WorkOrder,
  WorkOrderListParams,
  UUID,
  WorkOrderAssignmentCreate,
  WorkOrderWorkflowStep,
  WorkflowStepApprovalCreate,
  WorkflowStepListParams,
  ProjectWorkflowStepBatchItem,
  WorkflowStepOperationalRead,
} from "./types";

function buildQuery(
  params: Record<string, string | number | boolean | undefined | null>
): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }
    search.set(key, String(value));
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

/** GET /runtime/projects */
export function listProjects(
  params: ProjectListParams = {}
): Promise<PaginatedResponse<Project>> {
  return apiRequest<PaginatedResponse<Project>>(
    `/runtime/projects${buildQuery(params)}`
  );
}

/** GET /runtime/projects/{project_id}/work-orders */
export function listWorkOrders(
  projectId: UUID,
  params: WorkOrderListParams = {}
): Promise<PaginatedResponse<WorkOrder>> {
  return apiRequest<PaginatedResponse<WorkOrder>>(
    `/runtime/projects/${projectId}/work-orders${buildQuery(params)}`
  );
}

/** GET /runtime/projects/{project_id}/activity-instances */
export function listActivityInstances(
  projectId: UUID,
  params: ActivityInstanceListParams = {}
): Promise<PaginatedResponse<ActivityInstance>> {
  return apiRequest<PaginatedResponse<ActivityInstance>>(
    `/runtime/projects/${projectId}/activity-instances${buildQuery(params)}`
  );
}

/** GET /runtime/activity-instances/{id}/workflow-steps */
export function listWorkflowSteps(
  activityInstanceId: UUID,
  params: WorkflowStepListParams = {}
): Promise<PaginatedResponse<WorkflowStepOperationalRead>> {
  return apiRequest<PaginatedResponse<WorkflowStepOperationalRead>>(
    `/runtime/activity-instances/${activityInstanceId}/workflow-steps${buildQuery(params)}`
  );
}

/** GET /runtime/work-orders/{work_order_id}/daily-reports */
export function listDailyReports(
  workOrderId: UUID,
  params: DailyReportListParams = {}
): Promise<PaginatedResponse<DailyReport>> {
  return apiRequest<PaginatedResponse<DailyReport>>(
    `/runtime/work-orders/${workOrderId}/daily-reports${buildQuery(params)}`
  );
}

/** GET /runtime/projects/{project_id}/workflow-steps-batch */
export function listProjectWorkflowStepsBatch(
  projectId: UUID,
  params: { status?: string; limit?: number; offset?: number } = {}
): Promise<PaginatedResponse<ProjectWorkflowStepBatchItem>> {
  return apiRequest<PaginatedResponse<ProjectWorkflowStepBatchItem>>(
    `/runtime/projects/${projectId}/workflow-steps-batch${buildQuery(params)}`
  );
}

/** GET /runtime/projects/{project_id}/dashboard-summary */
export function getProjectDashboardSummary(
  projectId: UUID
): Promise<ProjectDashboardSummary> {
  return apiRequest<ProjectDashboardSummary>(
    `/runtime/projects/${projectId}/dashboard-summary`
  );
}

/** GET /runtime/projects/{project_id}/dashboard */
export function getProjectDashboard(
  projectId: UUID
): Promise<ProjectDashboard> {
  return apiRequest<ProjectDashboard>(
    `/runtime/projects/${projectId}/dashboard`
  );
}

/** GET /runtime/activity-instances/{activity_instance_id} */
export function getActivityInstanceRuntime(
  activityInstanceId: UUID
): Promise<ActivityInstanceRuntimeView> {
  return apiRequest<ActivityInstanceRuntimeView>(
    `/runtime/activity-instances/${activityInstanceId}`
  );
}

/** POST /runtime/work-orders/{work_order_id}/assign */
export function assignWorkOrder(
  workOrderId: UUID,
  payload: WorkOrderAssignmentCreate
): Promise<WorkOrderWorkflowStep> {
  return apiRequest<WorkOrderWorkflowStep>(
    `/runtime/work-orders/${workOrderId}/assign`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

/** POST /runtime/daily-reports */
export function submitDailyReport(
  payload: DailyReportCreate
): Promise<DailyReport> {
  return apiRequest<DailyReport>("/runtime/daily-reports", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** POST /runtime/workflow-steps/{workflow_step_id}/approve */
export function approveWorkflowStep(
  workflowStepId: UUID,
  payload: WorkflowStepApprovalCreate = {}
): Promise<Approval> {
  return apiRequest<Approval>(
    `/runtime/workflow-steps/${workflowStepId}/approve`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

/**
 * Phase 1 planning API — thin typed wrappers over the `/planning/*` endpoints.
 * Reuses the shared `apiRequest` HTTP client. All creates return Read models.
 */

import { apiRequest } from "@/lib/api/client";
import type {
  ActivityInstance,
  ActivityInstanceCreate,
  Location,
  LocationCreate,
  Project,
  ProjectCreate,
  WBSItem,
  WBSItemCreate,
  WorkOrder,
  WorkOrderCreate,
  WorkflowStep,
  WorkflowStepCreate,
} from "./types";

function post<TResponse, TPayload>(
  path: string,
  payload: TPayload
): Promise<TResponse> {
  return apiRequest<TResponse>(path, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createProject(payload: ProjectCreate): Promise<Project> {
  return post<Project, ProjectCreate>("/planning/projects", payload);
}

export function createWBSItem(payload: WBSItemCreate): Promise<WBSItem> {
  return post<WBSItem, WBSItemCreate>("/planning/wbs-items", payload);
}

export function createLocation(payload: LocationCreate): Promise<Location> {
  return post<Location, LocationCreate>("/planning/locations", payload);
}

export function createActivityInstance(
  payload: ActivityInstanceCreate
): Promise<ActivityInstance> {
  return post<ActivityInstance, ActivityInstanceCreate>(
    "/planning/activity-instances",
    payload
  );
}

export function createWorkflowStep(
  payload: WorkflowStepCreate
): Promise<WorkflowStep> {
  return post<WorkflowStep, WorkflowStepCreate>(
    "/planning/workflow-steps",
    payload
  );
}

export function createWorkOrder(
  payload: WorkOrderCreate
): Promise<WorkOrder> {
  return post<WorkOrder, WorkOrderCreate>("/planning/work-orders", payload);
}

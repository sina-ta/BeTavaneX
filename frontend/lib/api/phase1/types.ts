/**
 * Phase 1 transport DTOs — mirror of backend Pydantic Read/Create schemas.
 *
 * All identifiers are UUID strings (no numeric IDs). Date fields are ISO date
 * strings ("YYYY-MM-DD"); timestamps are ISO datetime strings. Decimal-backed
 * fields may arrive as a number or a string depending on the serializer, so
 * they are typed as `Decimalish` and should be normalized with `toNumber`.
 */

export type UUID = string;
export type ISODate = string;
export type ISODateTime = string;

/** A numeric value that the backend may serialize as number or string. */
export type Decimalish = number | string;

export function toNumber(value: Decimalish | null | undefined): number {
  if (value === null || value === undefined) {
    return 0;
  }
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

// ---------------------------------------------------------------------------
// Read models (responses)
// ---------------------------------------------------------------------------

export interface Project {
  id: UUID;
  code: string;
  name: string;
  description: string | null;
  status: string;
  planned_start: ISODate | null;
  planned_finish: ISODate | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface WBSItem {
  id: UUID;
  project_id: UUID;
  parent_id: UUID | null;
  code: string;
  name: string;
  description: string | null;
  level: number;
  status: string;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface Location {
  id: UUID;
  project_id: UUID;
  parent_id: UUID | null;
  code: string;
  name: string;
  description: string | null;
  level: number;
  status: string;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface ActivityInstance {
  id: UUID;
  project_id: UUID;
  wbs_item_id: UUID;
  location_id: UUID;
  code: string;
  name: string;
  planned_start: ISODate | null;
  planned_finish: ISODate | null;
  planned_duration_days: number | null;
  status: string;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface WorkflowStep {
  id: UUID;
  activity_instance_id: UUID;
  workflow_template_id: UUID | null;
  code: string;
  name: string;
  status: string;
  ready: boolean;
  progress_percent: Decimalish;
  planned_weight: Decimalish | null;
  planned_start: ISODate | null;
  planned_finish: ISODate | null;
  actual_start: ISODate | null;
  actual_finish: ISODate | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface WorkOrder {
  id: UUID;
  project_id: UUID;
  work_order_number: string;
  title: string;
  description: string | null;
  planned_date: ISODate;
  status: string;
  created_by: UUID | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface DailyReport {
  id: UUID;
  work_order_id: UUID;
  report_date: ISODate;
  status: string;
  summary: string | null;
  execution_notes: string | null;
  issue_notes: string | null;
  delay_notes: string | null;
  weather_notes: string | null;
  evidence_metadata: Record<string, unknown> | unknown[] | null;
  submitted_by: UUID | null;
  submitted_at: ISODateTime | null;
  reported_manpower: number | null;
  reported_equipment: number | null;
  reported_material_entries: number | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface Approval {
  id: UUID;
  workflow_step_id: UUID;
  approval_type: string;
  status: string;
  approval_date: ISODate | null;
  approved_by: UUID | null;
  approval_notes: string | null;
  rejection_reason: string | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface WorkOrderWorkflowStep {
  id: UUID;
  work_order_id: UUID;
  workflow_step_id: UUID;
  execution_weight: Decimalish;
  created_at: ISODateTime;
}

// ---------------------------------------------------------------------------
// Runtime composite views (GET /runtime/*)
// ---------------------------------------------------------------------------

export interface ProjectDashboard {
  project_id: UUID;
  project_progress: Decimalish;
  activity_instance_count: number;
  workflow_step_count: number;
  work_order_count: number;
}

export interface ActivityInstanceProgressSummary {
  activity_instance_progress: Decimalish;
  workflow_step_progress: Record<UUID, Decimalish>;
}

export interface ActivityInstanceRuntimeView {
  activity_instance: ActivityInstance | null;
  workflow_steps: WorkflowStep[];
  progress_summary: ActivityInstanceProgressSummary;
}

export interface Blocker {
  id: UUID;
  workflow_step_id: UUID;
  title: string;
  description: string | null;
  blocker_type: string;
  severity: string;
  status: string;
  detected_date: ISODate;
  resolved_date: ISODate | null;
  reported_by: UUID | null;
  root_cause: string | null;
  resolution_notes: string | null;
  created_at: ISODateTime;
  updated_at: ISODateTime;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface WorkflowStepOperationalRead {
  workflow_step: WorkflowStep;
  approvals: Approval[];
  blockers: Blocker[];
}

export interface ProjectWorkflowStepBatchItem {
  activity_instance_id: UUID;
  activity_code: string;
  activity_name: string;
  workflow_step: WorkflowStep;
  approvals: Approval[];
  blockers: Blocker[];
}

export interface ActivityInstanceProgressItem {
  activity_instance_id: UUID;
  code: string;
  name: string;
  status: string;
  progress_percent: Decimalish;
}

export interface WorkOrderStatusCount {
  status: string;
  count: number;
}

export interface ProjectDashboardSummary extends ProjectDashboard {
  activity_instances: ActivityInstanceProgressItem[];
  work_orders_by_status: WorkOrderStatusCount[];
}

export type RuntimeListParams = {
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_dir?: "asc" | "desc";
};

export type ProjectListParams = RuntimeListParams & {
  name?: string;
  status?: string;
};

export type ActivityInstanceListParams = RuntimeListParams & {
  wbs_item_id?: UUID;
  location_id?: UUID;
  status?: string;
};

export type WorkflowStepListParams = RuntimeListParams & {
  status?: string;
  ready?: boolean;
};

export type DailyReportListParams = RuntimeListParams & {
  status?: string;
  report_date_from?: ISODate;
  report_date_to?: ISODate;
};

export type WorkOrderListParams = RuntimeListParams & {
  status?: string;
  workflow_step_id?: UUID;
  planned_date_from?: ISODate;
  planned_date_to?: ISODate;
};

// ---------------------------------------------------------------------------
// Create payloads (requests)
// ---------------------------------------------------------------------------

export interface ProjectCreate {
  code: string;
  name: string;
  description?: string | null;
  status?: string;
  planned_start?: ISODate | null;
  planned_finish?: ISODate | null;
}

export interface WBSItemCreate {
  project_id: UUID;
  code: string;
  name: string;
  level: number;
  parent_id?: UUID | null;
  description?: string | null;
  status?: string;
}

export interface LocationCreate {
  project_id: UUID;
  code: string;
  name: string;
  level: number;
  parent_id?: UUID | null;
  description?: string | null;
  status?: string;
}

export interface ActivityInstanceCreate {
  project_id: UUID;
  wbs_item_id: UUID;
  location_id: UUID;
  code: string;
  name: string;
  planned_start?: ISODate | null;
  planned_finish?: ISODate | null;
  planned_duration_days?: number | null;
  status?: string;
}

export interface WorkflowStepCreate {
  activity_instance_id: UUID;
  code: string;
  name: string;
  status: string;
  workflow_template_id?: UUID | null;
  ready?: boolean;
  progress_percent?: Decimalish;
  planned_weight?: Decimalish | null;
  planned_start?: ISODate | null;
  planned_finish?: ISODate | null;
  actual_start?: ISODate | null;
  actual_finish?: ISODate | null;
}

export interface WorkOrderCreate {
  project_id: UUID;
  work_order_number: string;
  title: string;
  planned_date: ISODate;
  description?: string | null;
  status?: string;
  created_by?: UUID | null;
}

export interface WorkOrderAssignmentCreate {
  workflow_step_id: UUID;
  execution_weight: Decimalish;
}

export interface DailyReportCreate {
  work_order_id: UUID;
  report_date: ISODate;
  expected_work_order_updated_at?: ISODateTime | null;
  status?: string;
  summary?: string | null;
  execution_notes?: string | null;
  issue_notes?: string | null;
  delay_notes?: string | null;
  weather_notes?: string | null;
  evidence_metadata?: Record<string, unknown> | unknown[] | null;
  submitted_by?: UUID | null;
  submitted_at?: ISODateTime | null;
  reported_manpower?: number | null;
  reported_equipment?: number | null;
  reported_material_entries?: number | null;
}

export interface WorkflowStepApprovalCreate {
  approval_type?: string;
  approved_by?: UUID | null;
  approval_date?: ISODate | null;
  approval_notes?: string | null;
  expected_workflow_step_updated_at?: ISODateTime | null;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export type Phase1Role = "admin" | "supervisor" | "worker" | "investor";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AuthSession {
  accessToken: string;
  role: string;
  username: string;
}

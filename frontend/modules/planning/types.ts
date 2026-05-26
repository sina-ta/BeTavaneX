export type PlanningProjectType =
  | "residential_tower"
  | "commercial_building"
  | "mixed_use"
  | "industrial";

export type PlanningLocationType =
  | "tower"
  | "floor"
  | "zone"
  | "room"
  | "sector";

export type PlanningDependencyType = "FS" | "SS" | "FF";

export type PlanningResourceType =
  | "manpower"
  | "material"
  | "equipment";

export type PlanningActivityStatus =
  | "planned"
  | "ready"
  | "in_progress"
  | "blocked"
  | "completed";

export interface PlanningProject {
  id: string;
  title: string;
  projectType: PlanningProjectType;
  baselineMode: "prototype";
  createdAt: string;
}

export interface PlanningWbsTemplate {
  id: string;
  code: string;
  title: string;
  category: string;
  phase: string;
  description: string;
  repeatable: boolean;
  defaultDurationDays: number;
  defaultResourceHints: Partial<
    Record<PlanningResourceType, number>
  >;
}

export interface PlanningLocationNode {
  id: string;
  title: string;
  nodeType: PlanningLocationType;
  parentId: string | null;
}

export interface PlanningActivity {
  id: string;
  templateId: string;
  locationNodeId: string;
  title: string;
  workflowContext: string;
  plannedStart: string;
  plannedFinish: string;
  baselineStart: string;
  baselineFinish: string;
  plannedProgressPercent: number;
  actualProgressPercent: number;
  status: PlanningActivityStatus;
  delayNote: string;
  operationalComment: string;
}

export interface PlanningDependency {
  id: string;
  predecessorActivityId: string;
  successorActivityId: string;
  dependencyType: PlanningDependencyType;
  lagDays: number;
}

export interface PlanningResource {
  id: string;
  type: PlanningResourceType;
  title: string;
  unit: string;
  plannedQuantity: number;
  actualQuantity: number;
}

export interface PlanningAssignment {
  id: string;
  activityId: string;
  resourceId: string;
  plannedQuantity: number;
  actualQuantity: number;
  allocationStart: string;
  allocationFinish: string;
}

export interface PlanningProgressLog {
  id: string;
  activityId: string;
  plannedProgressPercent: number;
  actualProgressPercent: number;
  delayNote: string;
  operationalComment: string;
  manpowerUsed: number;
  materialUsage: number;
  equipmentHours: number;
  loggedAt: string;
}

export interface PlanningPrototypeState {
  project: PlanningProject | null;
  templatesLoaded: boolean;
  selectedTemplateIds: string[];
  locations: PlanningLocationNode[];
  activities: PlanningActivity[];
  dependencies: PlanningDependency[];
  resources: PlanningResource[];
  assignments: PlanningAssignment[];
  progressLogs: PlanningProgressLog[];
}

"use client";

/**
 * Session workspace registry for the Phase 1 vertical slice.
 *
 * The Phase 1 backend exposes only POST (planning) and GET-by-id (runtime) —
 * there are no list endpoints. To let users select entities they just created
 * (without pasting UUIDs), this context records every created entity for the
 * session and persists it to localStorage. React Context only — no Redux,
 * no Zustand, no React Query. This is UI navigation state, not a data cache.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";

import type {
  ActivityInstance,
  Approval,
  DailyReport,
  Location,
  Project,
  UUID,
  WBSItem,
  WorkOrder,
  WorkOrderWorkflowStep,
  WorkflowStep,
} from "@/lib/api/phase1/types";

const STORAGE_KEY = "betavanx.workspace";

type WorkspaceState = {
  projects: Project[];
  wbsItems: WBSItem[];
  locations: Location[];
  activityInstances: ActivityInstance[];
  workflowSteps: WorkflowStep[];
  workOrders: WorkOrder[];
  assignments: WorkOrderWorkflowStep[];
  dailyReports: DailyReport[];
  approvals: Approval[];
};

const EMPTY_STATE: WorkspaceState = {
  projects: [],
  wbsItems: [],
  locations: [],
  activityInstances: [],
  workflowSteps: [],
  workOrders: [],
  assignments: [],
  dailyReports: [],
  approvals: [],
};

type WorkspaceContextValue = WorkspaceState & {
  addProject: (entity: Project) => void;
  addWBSItem: (entity: WBSItem) => void;
  addLocation: (entity: Location) => void;
  addActivityInstance: (entity: ActivityInstance) => void;
  addWorkflowStep: (entity: WorkflowStep) => void;
  addWorkOrder: (entity: WorkOrder) => void;
  addAssignment: (entity: WorkOrderWorkflowStep) => void;
  addDailyReport: (entity: DailyReport) => void;
  addApproval: (entity: Approval) => void;
  reset: () => void;
  // Project-scoped selectors
  wbsItemsForProject: (projectId: UUID | null) => WBSItem[];
  locationsForProject: (projectId: UUID | null) => Location[];
  activityInstancesForProject: (projectId: UUID | null) => ActivityInstance[];
  workOrdersForProject: (projectId: UUID | null) => WorkOrder[];
  workflowStepsForProject: (projectId: UUID | null) => WorkflowStep[];
  assignmentsForStep: (workflowStepId: UUID) => WorkOrderWorkflowStep[];
  dailyReportsForWorkOrder: (workOrderId: UUID) => DailyReport[];
  approvalsForStep: (workflowStepId: UUID) => Approval[];
};

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

function upsert<T extends { id: UUID }>(list: T[], entity: T): T[] {
  const next = list.filter((item) => item.id !== entity.id);
  next.push(entity);
  return next;
}

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<WorkspaceState>(EMPTY_STATE);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<WorkspaceState>;
        setState({ ...EMPTY_STATE, ...parsed });
      }
    } catch {
      // Ignore corrupt workspace state; start clean.
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated || typeof window === "undefined") {
      return;
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state, hydrated]);

  const addProject = useCallback((entity: Project) => {
    setState((s) => ({ ...s, projects: upsert(s.projects, entity) }));
  }, []);
  const addWBSItem = useCallback((entity: WBSItem) => {
    setState((s) => ({ ...s, wbsItems: upsert(s.wbsItems, entity) }));
  }, []);
  const addLocation = useCallback((entity: Location) => {
    setState((s) => ({ ...s, locations: upsert(s.locations, entity) }));
  }, []);
  const addActivityInstance = useCallback((entity: ActivityInstance) => {
    setState((s) => ({
      ...s,
      activityInstances: upsert(s.activityInstances, entity),
    }));
  }, []);
  const addWorkflowStep = useCallback((entity: WorkflowStep) => {
    setState((s) => ({
      ...s,
      workflowSteps: upsert(s.workflowSteps, entity),
    }));
  }, []);
  const addWorkOrder = useCallback((entity: WorkOrder) => {
    setState((s) => ({ ...s, workOrders: upsert(s.workOrders, entity) }));
  }, []);
  const addAssignment = useCallback((entity: WorkOrderWorkflowStep) => {
    setState((s) => ({
      ...s,
      assignments: upsert(s.assignments, entity),
    }));
  }, []);
  const addDailyReport = useCallback((entity: DailyReport) => {
    setState((s) => ({
      ...s,
      dailyReports: upsert(s.dailyReports, entity),
    }));
  }, []);
  const addApproval = useCallback((entity: Approval) => {
    setState((s) => ({ ...s, approvals: upsert(s.approvals, entity) }));
  }, []);
  const reset = useCallback(() => setState(EMPTY_STATE), []);

  const value = useMemo<WorkspaceContextValue>(() => {
    const activityIdsForProject = (projectId: UUID | null) =>
      new Set(
        state.activityInstances
          .filter((a) => a.project_id === projectId)
          .map((a) => a.id)
      );

    return {
      ...state,
      addProject,
      addWBSItem,
      addLocation,
      addActivityInstance,
      addWorkflowStep,
      addWorkOrder,
      addAssignment,
      addDailyReport,
      addApproval,
      reset,
      wbsItemsForProject: (projectId) =>
        state.wbsItems.filter((w) => w.project_id === projectId),
      locationsForProject: (projectId) =>
        state.locations.filter((l) => l.project_id === projectId),
      activityInstancesForProject: (projectId) =>
        state.activityInstances.filter((a) => a.project_id === projectId),
      workOrdersForProject: (projectId) =>
        state.workOrders.filter((w) => w.project_id === projectId),
      workflowStepsForProject: (projectId) => {
        const ids = activityIdsForProject(projectId);
        return state.workflowSteps.filter((s) =>
          ids.has(s.activity_instance_id)
        );
      },
      assignmentsForStep: (workflowStepId) =>
        state.assignments.filter(
          (a) => a.workflow_step_id === workflowStepId
        ),
      dailyReportsForWorkOrder: (workOrderId) =>
        state.dailyReports.filter((r) => r.work_order_id === workOrderId),
      approvalsForStep: (workflowStepId) =>
        state.approvals.filter(
          (a) => a.workflow_step_id === workflowStepId
        ),
    };
  }, [
    state,
    addProject,
    addWBSItem,
    addLocation,
    addActivityInstance,
    addWorkflowStep,
    addWorkOrder,
    addAssignment,
    addDailyReport,
    addApproval,
    reset,
  ]);

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace(): WorkspaceContextValue {
  const context = useContext(WorkspaceContext);
  if (context === null) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return context;
}

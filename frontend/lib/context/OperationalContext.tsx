"use client";

/**
 * Operational session ledger for the Stage 16B vertical slice.
 *
 * The Phase 1 backend exposes no planning *list* endpoints, so entities created
 * during a session are tracked here in memory. This lets each step's dropdowns
 * be populated from previously created entities (no manual UUID entry) and
 * gives the console a runtime ledger to navigate. React Context only — no
 * Redux/Zustand/React Query. The ledger is per-session (cleared on reload).
 */

import {
  createContext,
  useCallback,
  useContext,
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
  WBSItem,
  WorkflowStep,
  WorkOrder,
  WorkOrderWorkflowStep,
} from "@/lib/api/phase1/types";

type OperationalSession = {
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

type OperationalContextValue = OperationalSession & {
  refreshKey: number;
  bumpRefresh: () => void;
  addProject: (entity: Project) => void;
  addWBSItem: (entity: WBSItem) => void;
  addLocation: (entity: Location) => void;
  addActivityInstance: (entity: ActivityInstance) => void;
  addWorkflowStep: (entity: WorkflowStep) => void;
  addWorkOrder: (entity: WorkOrder) => void;
  addAssignment: (entity: WorkOrderWorkflowStep) => void;
  addDailyReport: (entity: DailyReport) => void;
  addApproval: (entity: Approval) => void;
  setWorkflowStepStatus: (id: string, status: string) => void;
};

const EMPTY_SESSION: OperationalSession = {
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

const OperationalContext = createContext<OperationalContextValue | null>(null);

export function OperationalProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<OperationalSession>(EMPTY_SESSION);
  const [refreshKey, setRefreshKey] = useState(0);

  const bumpRefresh = useCallback(() => {
    setRefreshKey((key) => key + 1);
  }, []);

  const addProject = useCallback((entity: Project) => {
    setSession((s) => ({ ...s, projects: [...s.projects, entity] }));
  }, []);

  const addWBSItem = useCallback((entity: WBSItem) => {
    setSession((s) => ({ ...s, wbsItems: [...s.wbsItems, entity] }));
  }, []);

  const addLocation = useCallback((entity: Location) => {
    setSession((s) => ({ ...s, locations: [...s.locations, entity] }));
  }, []);

  const addActivityInstance = useCallback((entity: ActivityInstance) => {
    setSession((s) => ({
      ...s,
      activityInstances: [...s.activityInstances, entity],
    }));
  }, []);

  const addWorkflowStep = useCallback((entity: WorkflowStep) => {
    setSession((s) => ({
      ...s,
      workflowSteps: [...s.workflowSteps, entity],
    }));
  }, []);

  const addWorkOrder = useCallback((entity: WorkOrder) => {
    setSession((s) => ({ ...s, workOrders: [...s.workOrders, entity] }));
  }, []);

  const addAssignment = useCallback((entity: WorkOrderWorkflowStep) => {
    setSession((s) => ({ ...s, assignments: [...s.assignments, entity] }));
  }, []);

  const addDailyReport = useCallback((entity: DailyReport) => {
    setSession((s) => ({ ...s, dailyReports: [...s.dailyReports, entity] }));
  }, []);

  const addApproval = useCallback((entity: Approval) => {
    setSession((s) => ({ ...s, approvals: [...s.approvals, entity] }));
  }, []);

  const setWorkflowStepStatus = useCallback(
    (id: string, status: string) => {
      setSession((s) => ({
        ...s,
        workflowSteps: s.workflowSteps.map((step) =>
          step.id === id ? { ...step, status } : step
        ),
      }));
    },
    []
  );

  const value = useMemo<OperationalContextValue>(
    () => ({
      ...session,
      refreshKey,
      bumpRefresh,
      addProject,
      addWBSItem,
      addLocation,
      addActivityInstance,
      addWorkflowStep,
      addWorkOrder,
      addAssignment,
      addDailyReport,
      addApproval,
      setWorkflowStepStatus,
    }),
    [
      session,
      refreshKey,
      bumpRefresh,
      addProject,
      addWBSItem,
      addLocation,
      addActivityInstance,
      addWorkflowStep,
      addWorkOrder,
      addAssignment,
      addDailyReport,
      addApproval,
      setWorkflowStepStatus,
    ]
  );

  return (
    <OperationalContext.Provider value={value}>
      {children}
    </OperationalContext.Provider>
  );
}

export function useOperational(): OperationalContextValue {
  const context = useContext(OperationalContext);
  if (context === null) {
    throw new Error(
      "useOperational must be used within an OperationalProvider"
    );
  }
  return context;
}

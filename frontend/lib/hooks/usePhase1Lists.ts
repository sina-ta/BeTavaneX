"use client";

import { useCallback, useEffect, useState } from "react";

import {
  listActivityInstances,
  listProjectWorkflowStepsBatch,
  listWorkflowSteps,
  listWorkOrders,
} from "@/lib/api/phase1/runtime";
import type { EntityOption } from "@/components/forms/EntitySelect";
import type {
  ActivityInstance,
  PaginatedResponse,
  UUID,
  WorkOrder,
  WorkflowStepOperationalRead,
} from "@/lib/api/phase1/types";
import { useAsyncData } from "@/lib/hooks/useAsyncData";

const EMPTY_ACTIVITIES: PaginatedResponse<ActivityInstance> = {
  items: [],
  total: 0,
  limit: 0,
  offset: 0,
};

const EMPTY_STEPS: PaginatedResponse<WorkflowStepOperationalRead> = {
  items: [],
  total: 0,
  limit: 0,
  offset: 0,
};

const EMPTY_WORK_ORDERS: PaginatedResponse<WorkOrder> = {
  items: [],
  total: 0,
  limit: 0,
  offset: 0,
};

export function useWorkOrders(projectId: UUID | null) {
  const fetcher = useCallback(async () => {
    if (!projectId) {
      return EMPTY_WORK_ORDERS;
    }
    return listWorkOrders(projectId, { limit: 200 });
  }, [projectId]);

  return useAsyncData(fetcher);
}

export function useActivityInstances(projectId: UUID | null) {
  const fetcher = useCallback(async () => {
    if (!projectId) {
      return EMPTY_ACTIVITIES;
    }
    return listActivityInstances(projectId, { limit: 200 });
  }, [projectId]);

  return useAsyncData(fetcher);
}

export function useWorkflowSteps(activityInstanceId: UUID | null) {
  const fetcher = useCallback(async () => {
    if (!activityInstanceId) {
      return EMPTY_STEPS;
    }
    return listWorkflowSteps(activityInstanceId, { limit: 200 });
  }, [activityInstanceId]);

  return useAsyncData(fetcher);
}

export function useProjectWorkflowStepOptions(projectId: UUID | null) {
  const [options, setOptions] = useState<EntityOption[]>([]);
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "error">(
    "idle"
  );

  const reload = useCallback(async () => {
    if (!projectId) {
      setOptions([]);
      setStatus("idle");
      return;
    }
    setStatus("loading");
    try {
      const batch = await listProjectWorkflowStepsBatch(projectId, {
        limit: 500,
      });
      const next: EntityOption[] = batch.items.map((row) => ({
        value: row.workflow_step.id,
        label: `${row.activity_code} · ${row.workflow_step.code} — ${row.workflow_step.name}`,
        updatedAt: row.workflow_step.updated_at,
      }));
      setOptions(next);
      setStatus("ready");
    } catch {
      setOptions([]);
      setStatus("error");
    }
  }, [projectId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { options, status, reload };
}

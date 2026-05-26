"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  getWorkflowSuggestionNote,
  getWorkflowSuggestionsForTemplate,
  planningWbsTemplates,
} from "./data";
import type {
  PlanningActivity,
  PlanningAssignment,
  PlanningDependency,
  PlanningDependencyType,
  PlanningLocationNode,
  PlanningLocationType,
  PlanningProgressLog,
  PlanningProject,
  PlanningProjectType,
  PlanningPrototypeState,
  PlanningResource,
  PlanningResourceType,
  PlanningWbsTemplate,
} from "./types";

const STORAGE_KEY = "betavanx-planning-prototype-v1";

const emptyState: PlanningPrototypeState = {
  project: null,
  templatesLoaded: false,
  selectedTemplateIds: [],
  locations: [],
  activities: [],
  dependencies: [],
  resources: [],
  assignments: [],
  progressLogs: [],
};

function createId(prefix: string): string {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`;
}

function toDateKey(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function addDays(dateKey: string, days: number): string {
  const next = new Date(`${dateKey}T00:00:00`);
  next.setDate(next.getDate() + days);
  return toDateKey(next);
}

function defaultStartDate(): string {
  return toDateKey(new Date());
}

function buildSeedLocations(): PlanningLocationNode[] {
  const towerId = createId("loc");
  return [
    {
      id: towerId,
      title: "Tower A",
      nodeType: "tower",
      parentId: null,
    },
    {
      id: createId("loc"),
      title: "Floor 1",
      nodeType: "floor",
      parentId: towerId,
    },
    {
      id: createId("loc"),
      title: "Floor 2",
      nodeType: "floor",
      parentId: towerId,
    },
  ];
}

function deriveActivityStatus(
  progress: number,
  delayNote: string
): PlanningActivity["status"] {
  if (progress >= 100) {
    return "completed";
  }
  if (delayNote.trim()) {
    return "blocked";
  }
  if (progress > 0) {
    return "in_progress";
  }
  return "ready";
}

export function usePlanningPrototype() {
  const [state, setState] =
    useState<PlanningPrototypeState>(emptyState);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (!saved) {
      return;
    }

    try {
      const parsed = JSON.parse(
        saved
      ) as PlanningPrototypeState;
      setState(parsed);
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(state)
    );
  }, [state]);

  const activeTemplates = useMemo(() => {
    if (!state.templatesLoaded) {
      return [] as PlanningWbsTemplate[];
    }

    return planningWbsTemplates.filter((template) =>
      state.selectedTemplateIds.includes(template.id)
    );
  }, [state.selectedTemplateIds, state.templatesLoaded]);

  const getLocationPath = useCallback(
    (locationId: string): string => {
      const nodesById = new Map(
        state.locations.map((node) => [node.id, node])
      );
      const parts: string[] = [];
      let current = nodesById.get(locationId);

      while (current) {
        parts.unshift(current.title);
        current = current.parentId
          ? nodesById.get(current.parentId)
          : undefined;
      }

      return parts.join(" / ");
    },
    [state.locations]
  );

  const getTemplateById = useCallback(
    (templateId: string) =>
      planningWbsTemplates.find(
        (template) => template.id === templateId
      ) ?? null,
    []
  );

  const getActivityById = useCallback(
    (activityId: string) =>
      state.activities.find(
        (activity) => activity.id === activityId
      ) ?? null,
    [state.activities]
  );

  const initializeProject = useCallback(
    (
      title: string,
      projectType: PlanningProjectType
    ) => {
      const project: PlanningProject = {
        id: createId("project"),
        title,
        projectType,
        baselineMode: "prototype",
        createdAt: new Date().toISOString(),
      };

      setState((current) => ({
        ...current,
        project,
        locations:
          current.locations.length > 0
            ? current.locations
            : buildSeedLocations(),
      }));
    },
    []
  );

  const loadWbsTemplates = useCallback(() => {
    setState((current) => ({
      ...current,
      templatesLoaded: true,
      selectedTemplateIds:
        current.selectedTemplateIds.length > 0
          ? current.selectedTemplateIds
          : planningWbsTemplates.map(
              (template) => template.id
            ),
    }));
  }, []);

  const toggleTemplate = useCallback((templateId: string) => {
    setState((current) => {
      const exists =
        current.selectedTemplateIds.includes(templateId);

      return {
        ...current,
        selectedTemplateIds: exists
          ? current.selectedTemplateIds.filter(
              (id) => id !== templateId
            )
          : [...current.selectedTemplateIds, templateId],
      };
    });
  }, []);

  const addLocation = useCallback(
    (
      title: string,
      nodeType: PlanningLocationType,
      parentId: string | null
    ) => {
      const location: PlanningLocationNode = {
        id: createId("loc"),
        title,
        nodeType,
        parentId,
      };

      setState((current) => ({
        ...current,
        locations: [...current.locations, location],
      }));
    },
    []
  );

  const instantiateActivity = useCallback(
    (params: {
      templateId: string;
      locationNodeId: string;
      plannedStart?: string;
      workflowContext?: string;
    }) => {
      const template = getTemplateById(params.templateId);
      if (!template) {
        return null;
      }

      const locationPath = getLocationPath(
        params.locationNodeId
      );
      const plannedStart =
        params.plannedStart ?? defaultStartDate();
      const plannedFinish = addDays(
        plannedStart,
        Math.max(template.defaultDurationDays - 1, 0)
      );

      const activity: PlanningActivity = {
        id: createId("activity"),
        templateId: template.id,
        locationNodeId: params.locationNodeId,
        title: `${template.title} @ ${locationPath}`,
        workflowContext:
          params.workflowContext ?? template.title,
        plannedStart,
        plannedFinish,
        baselineStart: plannedStart,
        baselineFinish: plannedFinish,
        plannedProgressPercent: 0,
        actualProgressPercent: 0,
        status: "ready",
        delayNote: "",
        operationalComment: "",
      };

      setState((current) => ({
        ...current,
        activities: [...current.activities, activity],
      }));

      return activity;
    },
    [getLocationPath, getTemplateById]
  );

  const addDependency = useCallback(
    (
      predecessorActivityId: string,
      successorActivityId: string,
      dependencyType: PlanningDependencyType,
      lagDays: number
    ) => {
      if (
        predecessorActivityId === successorActivityId
      ) {
        return;
      }

      setState((current) => {
        const duplicate = current.dependencies.some(
          (dependency) =>
            dependency.predecessorActivityId ===
              predecessorActivityId &&
            dependency.successorActivityId ===
              successorActivityId &&
            dependency.dependencyType === dependencyType
        );

        if (duplicate) {
          return current;
        }

        const dependency: PlanningDependency = {
          id: createId("dep"),
          predecessorActivityId,
          successorActivityId,
          dependencyType,
          lagDays,
        };

        return {
          ...current,
          dependencies: [
            ...current.dependencies,
            dependency,
          ],
        };
      });
    },
    []
  );

  const instantiateSuggestedActivity = useCallback(
    (
      sourceActivityId: string,
      suggestedTemplateTitle: string
    ) => {
      const sourceActivity = getActivityById(sourceActivityId);
      if (!sourceActivity) {
        return null;
      }

      const suggestedTemplate =
        planningWbsTemplates.find(
          (template) =>
            template.title === suggestedTemplateTitle
        ) ?? null;

      if (!suggestedTemplate) {
        return null;
      }

      const created = instantiateActivity({
        templateId: suggestedTemplate.id,
        locationNodeId: sourceActivity.locationNodeId,
        plannedStart: addDays(
          sourceActivity.plannedFinish,
          1
        ),
        workflowContext: `${sourceActivity.workflowContext} -> ${suggestedTemplate.title}`,
      });

      if (created) {
        addDependency(
          sourceActivity.id,
          created.id,
          "FS",
          0
        );
      }

      return created;
    },
    [
      addDependency,
      getActivityById,
      instantiateActivity,
    ]
  );

  const moveActivityByDays = useCallback(
    (activityId: string, deltaDays: number) => {
      if (deltaDays === 0) {
        return;
      }

      setState((current) => ({
        ...current,
        activities: current.activities.map((activity) =>
          activity.id === activityId
            ? {
                ...activity,
                plannedStart: addDays(
                  activity.plannedStart,
                  deltaDays
                ),
                plannedFinish: addDays(
                  activity.plannedFinish,
                  deltaDays
                ),
              }
            : activity
        ),
      }));
    },
    []
  );

  const addAssignment = useCallback(
    (params: {
      activityId: string;
      resourceType: PlanningResourceType;
      title: string;
      unit: string;
      plannedQuantity: number;
      actualQuantity: number;
      allocationStart: string;
      allocationFinish: string;
    }) => {
      const resource: PlanningResource = {
        id: createId("resource"),
        type: params.resourceType,
        title: params.title,
        unit: params.unit,
        plannedQuantity: params.plannedQuantity,
        actualQuantity: params.actualQuantity,
      };

      const assignment: PlanningAssignment = {
        id: createId("assign"),
        activityId: params.activityId,
        resourceId: resource.id,
        plannedQuantity: params.plannedQuantity,
        actualQuantity: params.actualQuantity,
        allocationStart: params.allocationStart,
        allocationFinish: params.allocationFinish,
      };

      setState((current) => ({
        ...current,
        resources: [...current.resources, resource],
        assignments: [...current.assignments, assignment],
      }));
    },
    []
  );

  const addProgressUpdate = useCallback(
    (params: {
      activityId: string;
      plannedProgressPercent: number;
      actualProgressPercent: number;
      delayNote: string;
      operationalComment: string;
      manpowerUsed: number;
      materialUsage: number;
      equipmentHours: number;
    }) => {
      const log: PlanningProgressLog = {
        id: createId("log"),
        activityId: params.activityId,
        plannedProgressPercent:
          params.plannedProgressPercent,
        actualProgressPercent:
          params.actualProgressPercent,
        delayNote: params.delayNote,
        operationalComment:
          params.operationalComment,
        manpowerUsed: params.manpowerUsed,
        materialUsage: params.materialUsage,
        equipmentHours: params.equipmentHours,
        loggedAt: new Date().toISOString(),
      };

      setState((current) => ({
        ...current,
        progressLogs: [log, ...current.progressLogs],
        activities: current.activities.map((activity) =>
          activity.id === params.activityId
            ? {
                ...activity,
                plannedProgressPercent:
                  params.plannedProgressPercent,
                actualProgressPercent:
                  params.actualProgressPercent,
                delayNote: params.delayNote,
                operationalComment:
                  params.operationalComment,
                status: deriveActivityStatus(
                  params.actualProgressPercent,
                  params.delayNote
                ),
              }
            : activity
        ),
      }));
    },
    []
  );

  const getWorkflowSuggestions = useCallback(
    (activityId: string) => {
      const activity = getActivityById(activityId);
      if (!activity) {
        return {
          templates: [] as PlanningWbsTemplate[],
          note: "Select an activity to view next-path suggestions.",
        };
      }

      const template = getTemplateById(activity.templateId);
      if (!template) {
        return {
          templates: [] as PlanningWbsTemplate[],
          note: "Template context is not available.",
        };
      }

      const suggestions =
        getWorkflowSuggestionsForTemplate(template.title)
          .map((title) =>
            planningWbsTemplates.find(
              (candidate) =>
                candidate.title === title
            )
          )
          .filter(
            (
              candidate
            ): candidate is PlanningWbsTemplate =>
              Boolean(candidate)
          );

      return {
        templates: suggestions,
        note: getWorkflowSuggestionNote(template.title),
      };
    },
    [getActivityById, getTemplateById]
  );

  const resetPrototype = useCallback(() => {
    setState(emptyState);
  }, []);

  return {
    state,
    activeTemplates,
    initializeProject,
    loadWbsTemplates,
    toggleTemplate,
    addLocation,
    instantiateActivity,
    instantiateSuggestedActivity,
    addDependency,
    moveActivityByDays,
    addAssignment,
    addProgressUpdate,
    getLocationPath,
    getTemplateById,
    getActivityById,
    getWorkflowSuggestions,
    resetPrototype,
  };
}

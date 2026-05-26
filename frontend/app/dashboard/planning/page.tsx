"use client";

import { useEffect, useMemo, useState } from "react";

import KpiCard from "@/components/KpiCard";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import KPIGrid from "@/components/layout/primitives/KPIGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import PageHeader from "@/components/ui/PageHeader";
import {
  type CommonMessageKey,
  type Locale,
} from "@/i18n/config";
import { useI18n } from "@/i18n/LanguageProvider";
import {
  planningLocationTypes,
  planningProjectTypes,
  planningResourceTypes,
  planningWbsTemplatesByPhase,
} from "@/modules/planning/data";
import { usePlanningPrototype } from "@/modules/planning/usePlanningPrototype";
import type {
  PlanningActivity,
  PlanningDependencyType,
  PlanningDependency,
  PlanningLocationType,
  PlanningLocationNode,
  PlanningProjectType,
  PlanningResourceType,
} from "@/modules/planning/types";

const DAY_WIDTH = 40;

const projectTypeLabelKeys: Record<
  PlanningProjectType,
  CommonMessageKey
> = {
  residential_tower:
    "planning_project_residential_tower",
  commercial_building:
    "planning_project_commercial_building",
  mixed_use: "planning_project_mixed_use",
  industrial: "planning_project_industrial",
};

const locationTypeLabelKeys: Record<
  PlanningLocationType,
  CommonMessageKey
> = {
  tower: "planning_location_tower",
  floor: "planning_location_floor",
  zone: "planning_location_zone",
  room: "planning_location_room",
  sector: "planning_location_sector",
};

const resourceTypeLabelKeys: Record<
  PlanningResourceType,
  CommonMessageKey
> = {
  manpower: "planning_resource_manpower",
  material: "planning_resource_material",
  equipment: "planning_resource_equipment",
};

const statusLabelKeys: Record<
  PlanningActivity["status"],
  CommonMessageKey
> = {
  planned: "status_planned",
  ready: "status_ready",
  in_progress: "status_in_progress",
  blocked: "status_blocked",
  completed: "status_completed",
};

const dependencyLabelKeys: Record<
  PlanningDependencyType,
  CommonMessageKey
> = {
  FS: "dependency_fs",
  SS: "dependency_ss",
  FF: "dependency_ff",
};

function formatDateLabel(
  dateKey: string,
  locale: Locale
): string {
  return new Date(`${dateKey}T00:00:00`).toLocaleDateString(
    locale === "fa" ? "fa-IR" : "en-US",
    {
      month: "short",
      day: "numeric",
    }
  );
}

function dateKey(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function addDays(dateInput: string, days: number): string {
  const next = new Date(`${dateInput}T00:00:00`);
  next.setDate(next.getDate() + days);
  return dateKey(next);
}

function diffDays(start: string, end: string): number {
  const startTime = new Date(`${start}T00:00:00`).getTime();
  const endTime = new Date(`${end}T00:00:00`).getTime();
  return Math.round(
    (endTime - startTime) / (1000 * 60 * 60 * 24)
  );
}

function buildTimeline(
  activities: PlanningActivity[]
): string[] {
  const today = dateKey(new Date());

  if (activities.length === 0) {
    return Array.from({ length: 14 }, (_, index) =>
      addDays(today, index)
    );
  }

  const start = activities
    .map((activity) => activity.plannedStart)
    .sort()[0];
  const end = activities
    .map((activity) => activity.plannedFinish)
    .sort()
    .at(-1) ?? start;
  const totalDays = Math.max(diffDays(start, end) + 5, 14);

  return Array.from({ length: totalDays }, (_, index) =>
    addDays(start, index)
  );
}

function buildLocationChildren(
  locations: PlanningLocationNode[],
  parentId: string | null
) {
  return locations.filter(
    (location) => location.parentId === parentId
  );
}

type SimpleGanttProps = {
  activities: PlanningActivity[];
  dependencies: PlanningDependency[];
  selectedActivityId: string | null;
  locale: Locale;
  t: (key: CommonMessageKey) => string;
  onSelectActivity: (activityId: string) => void;
  onMoveActivity: (activityId: string, deltaDays: number) => void;
};

function SimpleGantt({
  activities,
  dependencies,
  selectedActivityId,
  locale,
  t,
  onSelectActivity,
  onMoveActivity,
}: SimpleGanttProps) {
  const timeline = useMemo(
    () => buildTimeline(activities),
    [activities]
  );

  const [dragState, setDragState] = useState<{
    activityId: string;
    startX: number;
    previewDays: number;
  } | null>(null);

  useEffect(() => {
    if (!dragState) {
      return;
    }

    const activeDragState = dragState;

    function handleMouseMove(event: MouseEvent) {
      const deltaPx =
        event.clientX - activeDragState.startX;
      const previewDays = Math.round(deltaPx / DAY_WIDTH);
      setDragState((current) =>
        current
          ? { ...current, previewDays }
          : current
      );
    }

    function handleMouseUp() {
      setDragState((current) => {
        if (current && current.previewDays !== 0) {
          onMoveActivity(
            current.activityId,
            current.previewDays
          );
        }
        return null;
      });
    }

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    return () => {
      window.removeEventListener(
        "mousemove",
        handleMouseMove
      );
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [dragState, onMoveActivity]);

  if (activities.length === 0) {
    return (
      <div className="planning-empty">
        {t("planning_gantt_empty")}
      </div>
    );
  }

  return (
    <div className="planning-gantt">
      <div className="planning-gantt-header">
        <div className="planning-gantt-title-cell">
          {t("planning_gantt_activity")}
        </div>
        <div className="planning-gantt-days">
          {timeline.map((day) => (
            <div
              key={day}
              className="planning-gantt-day"
              style={{ width: DAY_WIDTH }}
            >
              {formatDateLabel(day, locale)}
            </div>
          ))}
        </div>
      </div>

      <div className="planning-gantt-body">
        {activities.map((activity) => {
          const offsetDays = Math.max(
            diffDays(timeline[0], activity.plannedStart),
            0
          );
          const durationDays = Math.max(
            diffDays(
              activity.plannedStart,
              activity.plannedFinish
            ) + 1,
            1
          );
          const previewOffset =
            dragState?.activityId === activity.id
              ? dragState.previewDays
              : 0;
          const incomingDependencies = dependencies.filter(
            (dependency) =>
              dependency.successorActivityId === activity.id
          );

          return (
            <div
              key={activity.id}
              className={`planning-gantt-row ${
                selectedActivityId === activity.id
                  ? "planning-gantt-row--selected"
                  : ""
              }`}
              onClick={() => onSelectActivity(activity.id)}
            >
              <div className="planning-gantt-row-label">
                <div className="planning-gantt-row-title">
                  {activity.title}
                </div>
                <div className="planning-gantt-row-meta">
                  <span>{t(statusLabelKeys[activity.status])}</span>
                  {incomingDependencies.length > 0 && (
                    <span>
                      {incomingDependencies.length}{" "}
                      {t("planning_dependency_word")}
                    </span>
                  )}
                </div>
              </div>

              <div className="planning-gantt-row-track">
                {timeline.map((day) => (
                  <div
                    key={`${activity.id}-${day}`}
                    className="planning-gantt-cell"
                    style={{ width: DAY_WIDTH }}
                  />
                ))}

                <button
                  type="button"
                  className={`planning-gantt-bar planning-gantt-bar--${activity.status}`}
                  style={{
                    left:
                      (offsetDays + previewOffset) *
                      DAY_WIDTH,
                    width: durationDays * DAY_WIDTH - 6,
                  }}
                  onMouseDown={(event) => {
                    event.stopPropagation();
                    onSelectActivity(activity.id);
                    setDragState({
                      activityId: activity.id,
                      startX: event.clientX,
                      previewDays: 0,
                    });
                  }}
                >
                  <span className="planning-gantt-bar-label">
                    {activity.actualProgressPercent.toFixed(0)}%
                  </span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function PlanningPrototypePage() {
  const { locale, t } = useI18n();
  const {
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
  } = usePlanningPrototype();

  const formatProjectType = (
    value: PlanningProjectType
  ) => t(projectTypeLabelKeys[value]);

  const formatLocationType = (
    value: PlanningLocationType
  ) => t(locationTypeLabelKeys[value]);

  const formatResourceType = (
    value: PlanningResourceType
  ) => t(resourceTypeLabelKeys[value]);

  const [projectTitle, setProjectTitle] = useState(
    "BetavanX Prototype"
  );
  const [projectType, setProjectType] =
    useState<PlanningProjectType>(
      "residential_tower"
    );
  const [locationTitle, setLocationTitle] = useState("");
  const [locationType, setLocationType] =
    useState<PlanningLocationType>("zone");
  const [parentLocationId, setParentLocationId] =
    useState<string>("");
  const [templateSearch, setTemplateSearch] =
    useState("");
  const [selectedTemplateId, setSelectedTemplateId] =
    useState<string>("");
  const [selectedLocationId, setSelectedLocationId] =
    useState<string>("");
  const [plannedStart, setPlannedStart] = useState(
    dateKey(new Date())
  );
  const [selectedActivityId, setSelectedActivityId] =
    useState<string | null>(null);
  const [dependencyType, setDependencyType] =
    useState<PlanningDependencyType>("FS");
  const [predecessorId, setPredecessorId] = useState("");
  const [successorId, setSuccessorId] = useState("");
  const [dependencyLag, setDependencyLag] = useState("0");
  const [resourceType, setResourceType] =
    useState<PlanningResourceType>("manpower");
  const [resourceTitle, setResourceTitle] = useState("");
  const [resourceUnit, setResourceUnit] = useState("people");
  const [plannedQuantity, setPlannedQuantity] =
    useState("4");
  const [actualQuantity, setActualQuantity] =
    useState("0");
  const [allocationStart, setAllocationStart] =
    useState(dateKey(new Date()));
  const [allocationFinish, setAllocationFinish] =
    useState(addDays(dateKey(new Date()), 1));
  const [plannedProgress, setPlannedProgress] =
    useState("30");
  const [actualProgress, setActualProgress] =
    useState("10");
  const [delayNote, setDelayNote] = useState("");
  const [operationalComment, setOperationalComment] =
    useState("");
  const [manpowerUsed, setManpowerUsed] = useState("4");
  const [materialUsage, setMaterialUsage] =
    useState("0");
  const [equipmentHours, setEquipmentHours] =
    useState("0");

  useEffect(() => {
    if (
      !selectedTemplateId &&
      activeTemplates.length > 0
    ) {
      setSelectedTemplateId(activeTemplates[0].id);
    }
  }, [activeTemplates, selectedTemplateId]);

  useEffect(() => {
    if (
      !selectedLocationId &&
      state.locations.length > 0
    ) {
      setSelectedLocationId(state.locations[0].id);
      setParentLocationId(state.locations[0].id);
    }
  }, [selectedLocationId, state.locations]);

  useEffect(() => {
    if (
      !selectedActivityId &&
      state.activities.length > 0
    ) {
      setSelectedActivityId(state.activities[0].id);
    }
  }, [selectedActivityId, state.activities]);

  useEffect(() => {
    const unit =
      planningResourceTypes.find(
        (resource) => resource.value === resourceType
      )?.unit ?? "units";
    setResourceUnit(unit);
  }, [resourceType]);

  const selectedActivity = selectedActivityId
    ? getActivityById(selectedActivityId)
    : null;

  const selectedActivityAssignments = useMemo(() => {
    if (!selectedActivityId) {
      return [];
    }

    return state.assignments
      .filter(
        (assignment) =>
          assignment.activityId === selectedActivityId
      )
      .map((assignment) => {
        const resource = state.resources.find(
          (item) => item.id === assignment.resourceId
        );

        return {
          assignment,
          resource,
        };
      });
  }, [
    selectedActivityId,
    state.assignments,
    state.resources,
  ]);

  const selectedActivityLogs = useMemo(() => {
    if (!selectedActivityId) {
      return [];
    }

    return state.progressLogs.filter(
      (log) => log.activityId === selectedActivityId
    );
  }, [selectedActivityId, state.progressLogs]);

  const visibleTemplateGroups = useMemo(() => {
    const normalizedSearch =
      templateSearch.trim().toLowerCase();

    return planningWbsTemplatesByPhase
      .map((group) => ({
        phase: group.phase,
        templates: group.templates.filter((template) => {
          const inSelectedSet =
            !state.templatesLoaded ||
            state.selectedTemplateIds.includes(
              template.id
            );

          if (!inSelectedSet) {
            return false;
          }

          if (!normalizedSearch) {
            return true;
          }

          return (
            template.title
              .toLowerCase()
              .includes(normalizedSearch) ||
            template.description
              .toLowerCase()
              .includes(normalizedSearch)
          );
        }),
      }))
      .filter((group) => group.templates.length > 0);
  }, [
    state.selectedTemplateIds,
    state.templatesLoaded,
    templateSearch,
  ]);

  const workflowSuggestions = selectedActivityId
    ? getWorkflowSuggestions(selectedActivityId)
    : {
        templates: [],
        note: "Select an instantiated activity to see next-path suggestions.",
      };

  const sortedActivities = useMemo(
    () =>
      [...state.activities].sort((left, right) =>
        left.plannedStart.localeCompare(right.plannedStart)
      ),
    [state.activities]
  );

  return (
    <SectionContainer>
      <PageHeader
        title={t("planning_title")}
        subtitle={t("planning_subtitle")}
        eyebrow={t("page_planning")}
      />

      <KPIGrid columns={4}>
        <KpiCard
          title={t("planning_templates_loaded")}
          value={state.templatesLoaded ? activeTemplates.length : 0}
          footer={t("planning_operational_library")}
        />
        <KpiCard
          title={t("planning_locations")}
          value={state.locations.length}
          footer={t("planning_location_aware_execution")}
        />
        <KpiCard
          title={t("planning_activities")}
          value={state.activities.length}
          footer={t("planning_executable_instances")}
        />
        <KpiCard
          title={t("planning_progress_logs")}
          value={state.progressLogs.length}
          footer={t("planning_operational_truth")}
        />
      </KPIGrid>

      <DashboardGrid variant="split">
        <CompactCard title={t("planning_project_setup")}>
          <div className="planning-form-grid">
            <label className="input-group">
              <span className="input-label">
                {t("planning_project_title")}
              </span>
              <input
                className="input-base"
                value={projectTitle}
                onChange={(event) =>
                  setProjectTitle(event.target.value)
                }
              />
            </label>

            <label className="input-group">
              <span className="input-label">
                {t("planning_project_type")}
              </span>
              <select
                className="input-base"
                value={projectType}
                onChange={(event) =>
                  setProjectType(
                    event.target.value as PlanningProjectType
                  )
                }
              >
                {planningProjectTypes.map((option) => (
                  <option
                    key={option.value}
                    value={option.value}
                  >
                    {formatProjectType(option.value)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="planning-actions">
            <button
              type="button"
              className="button-primary"
              onClick={() =>
                initializeProject(
                  projectTitle,
                  projectType
                )
              }
            >
              {t("planning_create_project")}
            </button>
            <button
              type="button"
              className="button-ghost"
              onClick={loadWbsTemplates}
              disabled={!state.project}
            >
              {t("planning_load_wbs_templates")}
            </button>
            <button
              type="button"
              className="button-ghost"
              onClick={resetPrototype}
            >
              {t("planning_reset_prototype")}
            </button>
          </div>

          {state.project ? (
            <div className="planning-summary-block">
              <div className="planning-summary-item">
                <span className="planning-summary-label">
                  {t("planning_active_project")}
                </span>
                <strong>{state.project.title}</strong>
              </div>
              <div className="planning-summary-item">
                <span className="planning-summary-label">
                  {t("planning_type")}
                </span>
                <strong>
                  {formatProjectType(
                    state.project.projectType
                  )}
                </strong>
              </div>
            </div>
          ) : (
            <div className="planning-empty">
              {t("planning_project_empty")}
            </div>
          )}
        </CompactCard>

        <CompactCard title={t("planning_location_tree")}>
          <div className="planning-form-grid">
            <label className="input-group">
              <span className="input-label">
                {t("planning_location_title")}
              </span>
              <input
                className="input-base"
                value={locationTitle}
                onChange={(event) =>
                  setLocationTitle(event.target.value)
                }
                placeholder={t("planning_location_zone")}
              />
            </label>

            <label className="input-group">
              <span className="input-label">
                {t("planning_location_type")}
              </span>
              <select
                className="input-base"
                value={locationType}
                onChange={(event) =>
                  setLocationType(
                    event.target.value as PlanningLocationType
                  )
                }
              >
                {planningLocationTypes.map((option) => (
                  <option
                    key={option.value}
                    value={option.value}
                  >
                    {formatLocationType(option.value)}
                  </option>
                ))}
              </select>
            </label>

            <label className="input-group planning-form-grid--full">
              <span className="input-label">
                {t("planning_parent_location")}
              </span>
              <select
                className="input-base"
                value={parentLocationId}
                onChange={(event) =>
                  setParentLocationId(event.target.value)
                }
              >
                <option value="">{t("planning_root")}</option>
                {state.locations.map((location) => (
                  <option
                    key={location.id}
                    value={location.id}
                  >
                    {getLocationPath(location.id)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="planning-actions">
            <button
              type="button"
              className="button-primary"
              disabled={!locationTitle.trim()}
              onClick={() => {
                addLocation(
                  locationTitle.trim(),
                  locationType,
                  parentLocationId || null
                );
                setLocationTitle("");
              }}
            >
              {t("planning_add_location")}
            </button>
          </div>

          {state.locations.length === 0 ? (
            <div className="planning-empty">
              {t("planning_location_empty")}
            </div>
          ) : (
            <div className="planning-tree">
              {buildLocationChildren(
                state.locations,
                null
              ).map((node) => (
                <LocationTreeNode
                  key={node.id}
                  node={node}
                  locations={state.locations}
                  t={t}
                />
              ))}
            </div>
          )}
        </CompactCard>
      </DashboardGrid>

      <DashboardGrid variant="split">
        <CompactCard title={t("planning_wbs_browser")}>
          <label className="input-group">
            <span className="input-label">
              {t("planning_search")}
            </span>
            <input
              className="input-base"
              value={templateSearch}
              onChange={(event) =>
                setTemplateSearch(event.target.value)
              }
              placeholder={t(
                "planning_search_templates_placeholder"
              )}
            />
          </label>

          {!state.templatesLoaded ? (
            <div className="planning-empty">
              {t("planning_load_wbs_to_explore")}
            </div>
          ) : (
            <div className="planning-template-groups">
              {visibleTemplateGroups.map((group) => (
                <div key={group.phase}>
                  <div className="planning-phase-title">
                    {group.phase}
                  </div>
                  <div className="planning-template-list">
                    {group.templates.map((template) => {
                      const active =
                        state.selectedTemplateIds.includes(
                          template.id
                        );

                      return (
                        <div
                          key={template.id}
                          className={`planning-template-card ${
                            selectedTemplateId ===
                            template.id
                              ? "planning-template-card--selected"
                              : ""
                          }`}
                          onClick={() =>
                            setSelectedTemplateId(
                              template.id
                            )
                          }
                        >
                          <div className="planning-template-card-header">
                            <strong>{template.title}</strong>
                            <span className="planning-chip">
                              {template.defaultDurationDays}d
                            </span>
                          </div>
                          <span className="page-subtitle">
                            {template.description}
                          </span>
                          <label className="planning-checkbox-row">
                            <input
                              type="checkbox"
                              checked={active}
                              onChange={(event) => {
                                event.stopPropagation();
                                toggleTemplate(template.id);
                              }}
                            />
                            {t("planning_include_in_prototype")}
                          </label>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CompactCard>

        <CompactCard
          title={t("planning_activity_instantiation")}
        >
          <div className="planning-form-grid">
            <label className="input-group">
              <span className="input-label">
                {t("planning_wbs_template")}
              </span>
              <select
                className="input-base"
                value={selectedTemplateId}
                onChange={(event) =>
                  setSelectedTemplateId(event.target.value)
                }
              >
                <option value="">
                  {t("planning_select_template")}
                </option>
                {activeTemplates.map((template) => (
                  <option
                    key={template.id}
                    value={template.id}
                  >
                    {template.title}
                  </option>
                ))}
              </select>
            </label>

            <label className="input-group">
              <span className="input-label">
                {t("planning_location")}
              </span>
              <select
                className="input-base"
                value={selectedLocationId}
                onChange={(event) =>
                  setSelectedLocationId(event.target.value)
                }
              >
                <option value="">
                  {t("planning_select_location")}
                </option>
                {state.locations.map((location) => (
                  <option
                    key={location.id}
                    value={location.id}
                  >
                    {getLocationPath(location.id)}
                  </option>
                ))}
              </select>
            </label>

            <label className="input-group planning-form-grid--full">
              <span className="input-label">
                {t("planning_planned_start")}
              </span>
              <input
                type="date"
                className="input-base"
                value={plannedStart}
                onChange={(event) =>
                  setPlannedStart(event.target.value)
                }
              />
            </label>
          </div>

          <div className="planning-actions">
            <button
              type="button"
              className="button-primary"
              disabled={
                !selectedTemplateId || !selectedLocationId
              }
              onClick={() => {
                const created = instantiateActivity({
                  templateId: selectedTemplateId,
                  locationNodeId: selectedLocationId,
                  plannedStart,
                });
                if (created) {
                  setSelectedActivityId(created.id);
                }
              }}
            >
              {t("planning_generate_activity")}
            </button>
          </div>

          {selectedTemplateId && selectedLocationId ? (
            <div className="planning-preview">
              <span className="planning-summary-label">
                {t("planning_preview")}
              </span>
              <strong>
                {getTemplateById(selectedTemplateId)?.title} @{" "}
                {getLocationPath(selectedLocationId)}
              </strong>
            </div>
          ) : (
            <div className="planning-empty">
              {t("planning_select_template_location")}
            </div>
          )}
        </CompactCard>
      </DashboardGrid>

      <DashboardGrid variant="split">
        <CompactCard title={t("planning_workflow_suggestions")}>
          {selectedActivity ? (
            <>
              <div className="planning-preview">
                <span className="planning-summary-label">
                  {t("planning_current_activity")}
                </span>
                <strong>{selectedActivity.title}</strong>
                <span className="page-subtitle">
                  {locale === "fa"
                    ? t("planning_optional_next_activity")
                    : workflowSuggestions.note}
                </span>
              </div>

              {workflowSuggestions.templates.length === 0 ? (
                <div className="planning-empty">
                  {t("planning_no_suggestions")}
                </div>
              ) : (
                <div className="planning-suggestion-list">
                  {workflowSuggestions.templates.map(
                    (template) => (
                      <button
                        type="button"
                        key={template.id}
                        className="planning-suggestion-card"
                        onClick={() => {
                          const created =
                            instantiateSuggestedActivity(
                              selectedActivity.id,
                              template.title
                            );
                          if (created) {
                            setSelectedActivityId(
                              created.id
                            );
                          }
                        }}
                      >
                        <strong>{template.title}</strong>
                        <span className="page-subtitle">
                          {t(
                            "planning_optional_next_activity"
                          )}
                        </span>
                      </button>
                    )
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="planning-empty">
              {t("planning_workflow_empty")}
            </div>
          )}
        </CompactCard>

        <CompactCard
          title={t("planning_resource_assignment")}
        >
          {selectedActivity ? (
            <>
              <div className="planning-preview">
                <span className="planning-summary-label">
                  {t("planning_assign_to")}
                </span>
                <strong>{selectedActivity.title}</strong>
              </div>

              <div className="planning-form-grid">
                <label className="input-group">
                  <span className="input-label">
                    {t("planning_resource_type")}
                  </span>
                  <select
                    className="input-base"
                    value={resourceType}
                    onChange={(event) =>
                      setResourceType(
                        event.target.value as PlanningResourceType
                      )
                    }
                  >
                    {planningResourceTypes.map((option) => (
                      <option
                        key={option.value}
                        value={option.value}
                      >
                        {formatResourceType(option.value)}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_resource_name")}
                  </span>
                  <input
                    className="input-base"
                    value={resourceTitle}
                    onChange={(event) =>
                      setResourceTitle(
                        event.target.value
                      )
                    }
                    placeholder={t("planning_resource_manpower")}
                  />
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_planned_qty")}
                  </span>
                  <input
                    className="input-base"
                    type="number"
                    value={plannedQuantity}
                    onChange={(event) =>
                      setPlannedQuantity(
                        event.target.value
                      )
                    }
                  />
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_actual_qty")}
                  </span>
                  <input
                    className="input-base"
                    type="number"
                    value={actualQuantity}
                    onChange={(event) =>
                      setActualQuantity(
                        event.target.value
                      )
                    }
                  />
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_allocation_start")}
                  </span>
                  <input
                    className="input-base"
                    type="date"
                    value={allocationStart}
                    onChange={(event) =>
                      setAllocationStart(
                        event.target.value
                      )
                    }
                  />
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_allocation_finish")}
                  </span>
                  <input
                    className="input-base"
                    type="date"
                    value={allocationFinish}
                    onChange={(event) =>
                      setAllocationFinish(
                        event.target.value
                      )
                    }
                  />
                </label>
              </div>

              <div className="planning-actions">
                <button
                  type="button"
                  className="button-primary"
                  disabled={!resourceTitle.trim()}
                  onClick={() => {
                    addAssignment({
                      activityId: selectedActivity.id,
                      resourceType,
                      title: resourceTitle.trim(),
                      unit: resourceUnit,
                      plannedQuantity:
                        Number(plannedQuantity) || 0,
                      actualQuantity:
                        Number(actualQuantity) || 0,
                      allocationStart,
                      allocationFinish,
                    });
                    setResourceTitle("");
                  }}
                >
                  {t("planning_assign_resource")}
                </button>
              </div>

              <div className="planning-list">
                {selectedActivityAssignments.length === 0 ? (
                  <div className="planning-empty">
                    {t("planning_no_assignments")}
                  </div>
                ) : (
                  selectedActivityAssignments.map(
                    ({ assignment, resource }) => (
                      <div
                        key={assignment.id}
                        className="planning-list-item"
                      >
                        <strong>
                          {resource?.title ??
                            t("planning_resource_name")}
                        </strong>
                        <span className="page-subtitle">
                          {resource
                            ? formatResourceType(
                                resource.type
                              )
                            : t(
                                "planning_resource_name"
                              )}{" "}
                          · {t("planning_planned_qty")}{" "}
                          {assignment.plannedQuantity}{" "}
                          {resource?.unit}
                        </span>
                      </div>
                    )
                  )
                )}
              </div>
            </>
          ) : (
            <div className="planning-empty">
              {t("planning_resource_empty")}
            </div>
          )}
        </CompactCard>
      </DashboardGrid>

      <CompactCard title={t("planning_gantt_title")}>
        <SimpleGantt
          activities={sortedActivities}
          dependencies={state.dependencies}
          selectedActivityId={selectedActivityId}
          locale={locale}
          t={t}
          onSelectActivity={(activityId) =>
            setSelectedActivityId(activityId)
          }
          onMoveActivity={moveActivityByDays}
        />

        {state.activities.length > 1 && (
          <div className="planning-dependency-builder">
            <div className="planning-phase-title">
              {t("planning_create_simple_dependency")}
            </div>
            <div className="planning-form-grid">
              <label className="input-group">
                <span className="input-label">
                  {t("planning_predecessor")}
                </span>
                <select
                  className="input-base"
                  value={predecessorId}
                  onChange={(event) =>
                    setPredecessorId(event.target.value)
                  }
                >
                  <option value="">
                    {t("planning_select_activity")}
                  </option>
                  {state.activities.map((activity) => (
                    <option
                      key={activity.id}
                      value={activity.id}
                    >
                      {activity.title}
                    </option>
                  ))}
                </select>
              </label>

              <label className="input-group">
                <span className="input-label">
                  {t("planning_successor")}
                </span>
                <select
                  className="input-base"
                  value={successorId}
                  onChange={(event) =>
                    setSuccessorId(event.target.value)
                  }
                >
                  <option value="">
                    {t("planning_select_activity")}
                  </option>
                  {state.activities.map((activity) => (
                    <option
                      key={activity.id}
                      value={activity.id}
                    >
                      {activity.title}
                    </option>
                  ))}
                </select>
              </label>

              <label className="input-group">
                <span className="input-label">
                  {t("planning_dependency_type")}
                </span>
                <select
                  className="input-base"
                  value={dependencyType}
                  onChange={(event) =>
                  setDependencyType(
                    event.target.value as PlanningDependencyType
                  )
                  }
                >
                  <option value="FS">
                    {t("dependency_fs")}
                  </option>
                  <option value="SS">
                    {t("dependency_ss")}
                  </option>
                  <option value="FF">
                    {t("dependency_ff")}
                  </option>
                </select>
              </label>

              <label className="input-group">
                <span className="input-label">
                  {t("planning_lag")}
                </span>
                <input
                  className="input-base"
                  type="number"
                  value={dependencyLag}
                  onChange={(event) =>
                    setDependencyLag(event.target.value)
                  }
                />
              </label>
            </div>

            <div className="planning-actions">
              <button
                type="button"
                className="button-primary"
                disabled={!predecessorId || !successorId}
                onClick={() => {
                  addDependency(
                    predecessorId,
                    successorId,
                    dependencyType,
                    Number(dependencyLag) || 0
                  );
                  setPredecessorId("");
                  setSuccessorId("");
                  setDependencyLag("0");
                }}
              >
                {t("planning_create_dependency")}
              </button>
            </div>

            <div className="planning-list">
              {state.dependencies.map((dependency) => {
                const predecessor =
                  getActivityById(
                    dependency.predecessorActivityId
                  );
                const successor = getActivityById(
                  dependency.successorActivityId
                );

                return (
                  <div
                    key={dependency.id}
                    className="planning-list-item"
                  >
                    <strong>
                      {predecessor?.title ??
                        t("planning_gantt_activity")}{" "}
                      {t(
                        dependencyLabelKeys[
                          dependency.dependencyType
                        ]
                      )}{" "}
                      {successor?.title ??
                        t("planning_gantt_activity")}
                    </strong>
                    <span className="page-subtitle">
                      {t("planning_lag")}:{" "}
                      {dependency.lagDays}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </CompactCard>

      <DashboardGrid variant="split">
        <CompactCard title={t("planning_progress_update")}>
          {selectedActivity ? (
            <>
              <div className="planning-preview">
                <span className="planning-summary-label">
                  {t("planning_update_activity")}
                </span>
                <strong>{selectedActivity.title}</strong>
              </div>

              <div className="planning-form-grid">
                <label className="input-group">
                  <span className="input-label">
                    {t("planning_planned_percent")}
                  </span>
                  <input
                    className="input-base"
                    type="number"
                    min="0"
                    max="100"
                    value={plannedProgress}
                    onChange={(event) =>
                      setPlannedProgress(
                        event.target.value
                      )
                    }
                  />
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_actual_percent")}
                  </span>
                  <input
                    className="input-base"
                    type="number"
                    min="0"
                    max="100"
                    value={actualProgress}
                    onChange={(event) =>
                      setActualProgress(
                        event.target.value
                      )
                    }
                  />
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_manpower_used")}
                  </span>
                  <input
                    className="input-base"
                    type="number"
                    value={manpowerUsed}
                    onChange={(event) =>
                      setManpowerUsed(
                        event.target.value
                      )
                    }
                  />
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_material_usage")}
                  </span>
                  <input
                    className="input-base"
                    type="number"
                    value={materialUsage}
                    onChange={(event) =>
                      setMaterialUsage(
                        event.target.value
                      )
                    }
                  />
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_equipment_hours")}
                  </span>
                  <input
                    className="input-base"
                    type="number"
                    value={equipmentHours}
                    onChange={(event) =>
                      setEquipmentHours(
                        event.target.value
                      )
                    }
                  />
                </label>

                <label className="input-group">
                  <span className="input-label">
                    {t("planning_delay_note")}
                  </span>
                  <input
                    className="input-base"
                    value={delayNote}
                    onChange={(event) =>
                      setDelayNote(event.target.value)
                    }
                    placeholder={t(
                      "planning_date_placeholder_delay"
                    )}
                  />
                </label>

                <label className="input-group planning-form-grid--full">
                  <span className="input-label">
                    {t("planning_operational_comment")}
                  </span>
                  <textarea
                    className="input-base planning-textarea"
                    value={operationalComment}
                    onChange={(event) =>
                      setOperationalComment(
                        event.target.value
                      )
                    }
                    placeholder={t(
                      "planning_comment_placeholder"
                    )}
                  />
                </label>
              </div>

              <div className="planning-actions">
                <button
                  type="button"
                  className="button-primary"
                  onClick={() =>
                    addProgressUpdate({
                      activityId: selectedActivity.id,
                      plannedProgressPercent:
                        Number(plannedProgress) || 0,
                      actualProgressPercent:
                        Number(actualProgress) || 0,
                      delayNote,
                      operationalComment,
                      manpowerUsed:
                        Number(manpowerUsed) || 0,
                      materialUsage:
                        Number(materialUsage) || 0,
                      equipmentHours:
                        Number(equipmentHours) || 0,
                    })
                  }
                >
                  {t("planning_add_progress_log")}
                </button>
              </div>
            </>
          ) : (
            <div className="planning-empty">
              {t("planning_progress_empty")}
            </div>
          )}
        </CompactCard>

        <CompactCard title={t("planning_operational_feed")}>
          <div className="planning-list">
            {state.progressLogs.length === 0 ? (
              <div className="planning-empty">
                {t("planning_feed_empty")}
              </div>
            ) : (
              state.progressLogs.map((log) => {
                const activity = getActivityById(
                  log.activityId
                );

                return (
                  <div
                    key={log.id}
                    className="planning-list-item"
                  >
                    <strong>
                      {activity?.title ??
                        t("planning_gantt_activity")}
                    </strong>
                    <span className="page-subtitle">
                      {t("planning_planned_percent")}{" "}
                      {log.plannedProgressPercent}% ·{" "}
                      {t("planning_actual_percent")}{" "}
                      {log.actualProgressPercent}%
                    </span>
                    {(log.delayNote ||
                      log.operationalComment) && (
                      <span className="page-subtitle">
                        {log.delayNote ||
                          log.operationalComment}
                      </span>
                    )}
                  </div>
                );
              })
            )}
          </div>

          {selectedActivity && selectedActivityLogs.length > 0 && (
            <>
              <div className="planning-phase-title">
                {t("planning_selected_activity_logs")}
              </div>
              <div className="planning-list">
                {selectedActivityLogs.map((log) => (
                  <div
                    key={log.id}
                    className="planning-list-item"
                  >
                    <strong>
                      {new Date(
                        log.loggedAt
                      ).toLocaleString(
                        locale === "fa" ? "fa-IR" : "en-US"
                      )}
                    </strong>
                    <span className="page-subtitle">
                      {t("planning_actual_percent")}{" "}
                      {log.actualProgressPercent}% ·{" "}
                      {t("planning_manpower_used")}{" "}
                      {log.manpowerUsed}
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </CompactCard>
      </DashboardGrid>
    </SectionContainer>
  );
}

function LocationTreeNode({
  node,
  locations,
  t,
}: {
  node: PlanningLocationNode;
  locations: PlanningLocationNode[];
  t: (key: CommonMessageKey) => string;
}) {
  const children = buildLocationChildren(
    locations,
    node.id
  );

  return (
    <div className="planning-tree-node">
      <div className="planning-tree-node-label">
        <strong>{node.title}</strong>
        <span className="planning-chip">
          {t(locationTypeLabelKeys[node.nodeType])}
        </span>
      </div>

      {children.length > 0 && (
        <div className="planning-tree-node-children">
          {children.map((child) => (
            <LocationTreeNode
              key={child.id}
              node={child}
              locations={locations}
              t={t}
            />
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

import { useState } from "react";
import Link from "next/link";

import {
  createActivityInstance,
  createWorkflowStep,
} from "@/lib/api/phase1/planning";
import RoleGate from "@/components/auth/RoleGate";
import { useProject } from "@/lib/context/ProjectContext";
import { useWorkspace } from "@/lib/context/WorkspaceContext";
import { useActivityInstances } from "@/lib/hooks/usePhase1Lists";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import FormField from "@/components/forms/FormField";
import FormGrid from "@/components/forms/FormGrid";
import FormLayout from "@/components/forms/FormLayout";
import TextInput from "@/components/forms/TextInput";
import SelectInput from "@/components/forms/SelectInput";
import EntitySelect from "@/components/forms/EntitySelect";
import SubmitButton from "@/components/forms/SubmitButton";
import FormError from "@/components/forms/FormError";
import FormSuccess from "@/components/forms/FormSuccess";
import PageHeader from "@/components/ui/PageHeader";
import CompactCard from "@/components/layout/primitives/CompactCard";
import DashboardGrid from "@/components/layout/primitives/DashboardGrid";
import SectionContainer from "@/components/layout/primitives/SectionContainer";
import { SliceNav } from "@/app/dashboard/console/page";

const ACTIVITY_STATUSES = ["ACTIVE", "COMPLETED", "CANCELLED"];
const STEP_STATUSES = [
  "PLANNED",
  "IN_PROGRESS",
  "INSPECTION_PENDING",
  "INSPECTION_FAILED",
  "REWORK_REQUIRED",
  "COMPLETED",
  "APPROVED",
];

export default function ConsoleActivityPage() {
  const { selectedProjectId } = useProject();

  return (
    <SectionContainer>
      <PageHeader
        title="Activities & Workflow Steps"
        subtitle="Instantiate executable activities under WBS × Location, then define their workflow steps."
        eyebrow="Vertical Slice"
      />

      <SliceNav current="activity" />

      {!selectedProjectId ? (
        <CompactCard title="No project selected">
          <p className="page-subtitle">
            Go to{" "}
            <Link href="/dashboard/console" className="text-blue-400 hover:underline">
              Planning Bootstrap
            </Link>{" "}
            and select or create a project first.
          </p>
        </CompactCard>
      ) : (
        <>
          <RoleGate allow="plan">
            <DashboardGrid variant="split">
              <CreateActivityForm projectId={selectedProjectId} />
              <CreateWorkflowStepForm projectId={selectedProjectId} />
            </DashboardGrid>
          </RoleGate>

          <ActivityRegistry projectId={selectedProjectId} />

          <p className="page-subtitle">
            Next:{" "}
            <Link
              href="/dashboard/console/execution?focus=assign"
              className="text-blue-400 hover:underline"
            >
              Assign work orders & submit reports
            </Link>
          </p>
        </>
      )}
    </SectionContainer>
  );
}

// ---------------------------------------------------------------------------

function CreateActivityForm({ projectId }: { projectId: string }) {
  const workspace = useWorkspace();
  const [wbsItemId, setWbsItemId] = useState("");
  const [locationId, setLocationId] = useState("");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [plannedStart, setPlannedStart] = useState("");
  const [plannedFinish, setPlannedFinish] = useState("");
  const [durationDays, setDurationDays] = useState("");
  const [status, setStatus] = useState("ACTIVE");

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: createActivityInstance,
    onSuccess: (activity) => {
      workspace.addActivityInstance(activity);
      setCode("");
      setName("");
    },
  });

  return (
    <FormLayout title="4 · Create Activity Instance">
      <form
        className="flex flex-col gap-8"
        onSubmit={(event) => {
          event.preventDefault();
          const errors: Record<string, string> = {};
          if (!wbsItemId) errors.wbs_item_id = "WBS item is required";
          if (!locationId) errors.location_id = "Location is required";
          if (!code.trim()) errors.code = "Code is required";
          if (!name.trim()) errors.name = "Name is required";

          handleSubmit(
            Object.keys(errors).length
              ? { success: false, errors }
              : {
                  success: true,
                  data: {
                    project_id: projectId,
                    wbs_item_id: wbsItemId,
                    location_id: locationId,
                    code: code.trim(),
                    name: name.trim(),
                    planned_start: plannedStart || null,
                    planned_finish: plannedFinish || null,
                    planned_duration_days: durationDays
                      ? Number(durationDays)
                      : null,
                    status,
                  },
                },
            "Activity instance created"
          );
        }}
      >
        <FormField label="WBS Item" error={validationErrors.wbs_item_id}>
          <EntitySelect
            value={wbsItemId}
            placeholder="Select WBS item…"
            onChange={(e) => setWbsItemId(e.target.value)}
            options={workspace
              .wbsItemsForProject(projectId)
              .map((w) => ({ value: w.id, label: `${w.code} — ${w.name}` }))}
          />
        </FormField>
        <FormField label="Location" error={validationErrors.location_id}>
          <EntitySelect
            value={locationId}
            placeholder="Select location…"
            onChange={(e) => setLocationId(e.target.value)}
            options={workspace
              .locationsForProject(projectId)
              .map((l) => ({ value: l.id, label: `${l.code} — ${l.name}` }))}
          />
        </FormField>
        <FormGrid>
          <FormField label="Code" error={validationErrors.code}>
            <TextInput
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="ACT-1"
            />
          </FormField>
          <FormField label="Name" error={validationErrors.name}>
            <TextInput
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Pour slab L1-ZA"
            />
          </FormField>
          <FormField label="Planned Start">
            <TextInput
              type="date"
              value={plannedStart}
              onChange={(e) => setPlannedStart(e.target.value)}
            />
          </FormField>
          <FormField label="Planned Finish">
            <TextInput
              type="date"
              value={plannedFinish}
              onChange={(e) => setPlannedFinish(e.target.value)}
            />
          </FormField>
          <FormField label="Duration (days)">
            <TextInput
              type="number"
              value={durationDays}
              onChange={(e) => setDurationDays(e.target.value)}
              placeholder="5"
            />
          </FormField>
          <FormField label="Status">
            <SelectInput
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              options={ACTIVITY_STATUSES}
            />
          </FormField>
        </FormGrid>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />
        <SubmitButton
          title="Create Activity Instance"
          loading={isSubmitting}
        />
      </form>
    </FormLayout>
  );
}

function CreateWorkflowStepForm({ projectId }: { projectId: string }) {
  const workspace = useWorkspace();
  const { data: activityPage } = useActivityInstances(projectId);
  const serverActivities = activityPage?.items ?? [];
  const [activityInstanceId, setActivityInstanceId] = useState("");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [status, setStatus] = useState("PLANNED");
  const [ready, setReady] = useState(false);
  const [progressPercent, setProgressPercent] = useState("0");
  const [plannedWeight, setPlannedWeight] = useState("");

  const {
    validationErrors,
    apiError,
    successMessage,
    isSubmitting,
    handleSubmit,
  } = useFormSubmit({
    submit: createWorkflowStep,
    onSuccess: (step) => {
      workspace.addWorkflowStep(step);
      setCode("");
      setName("");
    },
  });

  return (
    <FormLayout title="5 · Create Workflow Step">
      <form
        className="flex flex-col gap-8"
        onSubmit={(event) => {
          event.preventDefault();
          const errors: Record<string, string> = {};
          if (!activityInstanceId)
            errors.activity_instance_id = "Activity is required";
          if (!code.trim()) errors.code = "Code is required";
          if (!name.trim()) errors.name = "Name is required";

          handleSubmit(
            Object.keys(errors).length
              ? { success: false, errors }
              : {
                  success: true,
                  data: {
                    activity_instance_id: activityInstanceId,
                    code: code.trim(),
                    name: name.trim(),
                    status,
                    ready,
                    progress_percent: Number(progressPercent) || 0,
                    planned_weight: plannedWeight
                      ? Number(plannedWeight)
                      : null,
                  },
                },
            "Workflow step created"
          );
        }}
      >
        <FormField
          label="Activity Instance"
          error={validationErrors.activity_instance_id}
        >
          <EntitySelect
            value={activityInstanceId}
            placeholder="Select activity…"
            onChange={(e) => setActivityInstanceId(e.target.value)}
            options={(serverActivities.length > 0
              ? serverActivities
              : workspace.activityInstancesForProject(projectId)
            ).map((a) => ({ value: a.id, label: `${a.code} — ${a.name}` }))}
          />
        </FormField>
        <FormGrid>
          <FormField label="Code" error={validationErrors.code}>
            <TextInput
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="STEP-1"
            />
          </FormField>
          <FormField label="Name" error={validationErrors.name}>
            <TextInput
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Formwork"
            />
          </FormField>
          <FormField label="Status">
            <SelectInput
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              options={STEP_STATUSES}
            />
          </FormField>
          <FormField label="Planned Weight (0–100)">
            <TextInput
              type="number"
              value={plannedWeight}
              onChange={(e) => setPlannedWeight(e.target.value)}
              placeholder="25"
            />
          </FormField>
          <FormField label="Progress %">
            <TextInput
              type="number"
              value={progressPercent}
              onChange={(e) => setProgressPercent(e.target.value)}
              placeholder="0"
            />
          </FormField>
          <FormField label="Ready">
            <label
              className="flex items-center gap-3 text-sm text-gray-300"
              style={{ paddingTop: 12 }}
            >
              <input
                type="checkbox"
                checked={ready}
                onChange={(e) => setReady(e.target.checked)}
              />
              Mark step ready
            </label>
          </FormField>
        </FormGrid>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />
        <SubmitButton title="Create Workflow Step" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}

function ActivityRegistry({ projectId }: { projectId: string }) {
  const { data: activityPage, status, reload } =
    useActivityInstances(projectId);
  const activities = activityPage?.items ?? [];

  return (
    <CompactCard title="Activity Instances">
      {status === "loading" && (
        <p className="page-subtitle">Loading activities…</p>
      )}
      {activities.length === 0 && status !== "loading" ? (
        <p className="page-subtitle">
          No activity instances yet. Create one above.
        </p>
      ) : (
        <div className="planning-list">
          {activities.map((activity) => (
            <div key={activity.id} className="planning-list-item">
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 12,
                }}
              >
                <strong>
                  {activity.code} — {activity.name}
                </strong>
                <Link
                  href={`/dashboard/activity-instances/${activity.id}`}
                  className="text-blue-400 text-xs font-medium hover:underline"
                >
                  Runtime view →
                </Link>
              </div>
              <span className="page-subtitle">status {activity.status}</span>
            </div>
          ))}
        </div>
      )}
      {status === "error" && (
        <button type="button" className="button-ghost" onClick={reload}>
          Retry load
        </button>
      )}
    </CompactCard>
  );
}

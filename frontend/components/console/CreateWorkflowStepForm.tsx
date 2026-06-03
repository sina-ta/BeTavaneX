"use client";

import { useState } from "react";

import FormLayout from "@/components/forms/FormLayout";
import FormGrid from "@/components/forms/FormGrid";
import FormField from "@/components/forms/FormField";
import TextInput from "@/components/forms/TextInput";
import SelectInput from "@/components/forms/SelectInput";
import SubmitButton from "@/components/forms/SubmitButton";
import FormError from "@/components/forms/FormError";
import FormSuccess from "@/components/forms/FormSuccess";
import EntitySelect from "@/components/console/EntitySelect";
import NoProjectNotice from "@/components/console/NoProjectNotice";
import { createWorkflowStep } from "@/lib/api/phase1/planning";
import type { WorkflowStep, WorkflowStepCreate } from "@/lib/api/phase1/types";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

const WORKFLOW_STEP_STATUSES = [
  "PLANNED",
  "IN_PROGRESS",
  "COMPLETED",
  "INSPECTION_PENDING",
  "INSPECTION_FAILED",
  "REWORK_REQUIRED",
  "APPROVED",
];

export default function CreateWorkflowStepForm() {
  const {
    activityInstances,
    addWorkflowStep,
    bumpRefresh,
  } = useOperational();
  const { selectedProjectId } = useProject();

  const [activityInstanceId, setActivityInstanceId] = useState("");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [status, setStatus] = useState("PLANNED");
  const [plannedWeight, setPlannedWeight] = useState("");
  const [ready, setReady] = useState(false);

  const { validationErrors, apiError, successMessage, isSubmitting, handleSubmit } =
    useFormSubmit<WorkflowStepCreate, WorkflowStep>({
      submit: createWorkflowStep,
      onSuccess: (item) => {
        addWorkflowStep(item);
        bumpRefresh();
        setCode("");
        setName("");
        setStatus("PLANNED");
        setPlannedWeight("");
        setReady(false);
      },
    });

  if (!selectedProjectId) {
    return <NoProjectNotice title="5 · Create Workflow Step" />;
  }

  const activityOptions = activityInstances
    .filter((item) => item.project_id === selectedProjectId)
    .map((item) => ({ value: item.id, label: `${item.code} · ${item.name}` }));

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: Record<string, string> = {};
    if (!activityInstanceId) {
      errors.activity_instance_id = "Select an activity instance";
    }
    if (!code.trim()) errors.code = "Code is required";
    if (!name.trim()) errors.name = "Name is required";

    let weight: number | null = null;
    if (plannedWeight.trim()) {
      weight = Number(plannedWeight);
      if (!Number.isFinite(weight) || weight < 0 || weight > 100) {
        errors.planned_weight = "Planned weight must be between 0 and 100";
      }
    }

    if (Object.keys(errors).length > 0) {
      handleSubmit({ success: false, errors });
      return;
    }

    const payload: WorkflowStepCreate = {
      activity_instance_id: activityInstanceId,
      code: code.trim(),
      name: name.trim(),
      status,
      ready,
      planned_weight: weight,
    };

    handleSubmit({ success: true, data: payload }, "Workflow step created");
  }

  return (
    <FormLayout title="5 · Create Workflow Step">
      <form onSubmit={onSubmit} className="flex flex-col gap-8">
        <FormGrid>
          <EntitySelect
            label="Activity Instance"
            value={activityInstanceId}
            onChange={setActivityInstanceId}
            options={activityOptions}
            error={validationErrors.activity_instance_id}
          />

          <FormField label="Status">
            <SelectInput
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              options={WORKFLOW_STEP_STATUSES}
            />
          </FormField>

          <FormField label="Code" error={validationErrors.code}>
            <TextInput
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="STEP-01"
            />
          </FormField>

          <FormField label="Name" error={validationErrors.name}>
            <TextInput
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Rebar fixing"
            />
          </FormField>

          <FormField
            label="Planned Weight (0–100)"
            error={validationErrors.planned_weight}
          >
            <TextInput
              type="number"
              value={plannedWeight}
              onChange={(e) => setPlannedWeight(e.target.value)}
              placeholder="25"
            />
          </FormField>

          <FormField label="Ready">
            <label className="flex items-center gap-3 text-sm text-gray-300">
              <input
                type="checkbox"
                checked={ready}
                onChange={(e) => setReady(e.target.checked)}
              />
              Mark step as ready for execution
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

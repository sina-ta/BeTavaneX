"use client";

import { useState } from "react";

import FormLayout from "@/components/forms/FormLayout";
import FormGrid from "@/components/forms/FormGrid";
import FormField from "@/components/forms/FormField";
import TextInput from "@/components/forms/TextInput";
import TextareaInput from "@/components/forms/TextareaInput";
import SubmitButton from "@/components/forms/SubmitButton";
import FormError from "@/components/forms/FormError";
import FormSuccess from "@/components/forms/FormSuccess";
import EntitySelect from "@/components/console/EntitySelect";
import NoProjectNotice from "@/components/console/NoProjectNotice";
import { approveWorkflowStep } from "@/lib/api/phase1/runtime";
import type {
  Approval,
  WorkflowStepApprovalCreate,
} from "@/lib/api/phase1/types";
import { useFormSubmit } from "@/lib/hooks/useFormSubmit";
import { useOperational } from "@/lib/context/OperationalContext";
import { useProject } from "@/lib/context/ProjectContext";

type ApproveInput = {
  workflowStepId: string;
  payload: WorkflowStepApprovalCreate;
};

export default function ApproveWorkflowStepForm() {
  const {
    workflowSteps,
    activityInstances,
    addApproval,
    setWorkflowStepStatus,
    bumpRefresh,
  } = useOperational();
  const { selectedProjectId } = useProject();

  const [workflowStepId, setWorkflowStepId] = useState("");
  const [approvalType, setApprovalType] = useState("FINAL");
  const [approvalDate, setApprovalDate] = useState("");
  const [approvalNotes, setApprovalNotes] = useState("");

  const { validationErrors, apiError, successMessage, isSubmitting, handleSubmit } =
    useFormSubmit<ApproveInput, Approval>({
      submit: ({ workflowStepId: id, payload }) =>
        approveWorkflowStep(id, payload),
      onSuccess: (approval) => {
        addApproval(approval);
        setWorkflowStepStatus(approval.workflow_step_id, "APPROVED");
        bumpRefresh();
        setApprovalNotes("");
      },
    });

  if (!selectedProjectId) {
    return <NoProjectNotice title="9 · Approve Workflow Step" />;
  }

  const projectActivityIds = new Set(
    activityInstances
      .filter((item) => item.project_id === selectedProjectId)
      .map((item) => item.id)
  );
  const stepOptions = workflowSteps
    .filter((step) => projectActivityIds.has(step.activity_instance_id))
    .map((step) => ({
      value: step.id,
      label: `${step.code} · ${step.name} (${step.status})`,
    }));

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const errors: Record<string, string> = {};
    if (!workflowStepId) errors.workflow_step_id = "Select a workflow step";
    if (!approvalType.trim()) errors.approval_type = "Approval type is required";

    if (Object.keys(errors).length > 0) {
      handleSubmit({ success: false, errors });
      return;
    }

    handleSubmit(
      {
        success: true,
        data: {
          workflowStepId,
          payload: {
            approval_type: approvalType.trim(),
            approval_date: approvalDate || null,
            approval_notes: approvalNotes.trim() || null,
          },
        },
      },
      "Workflow step approved"
    );
  }

  return (
    <FormLayout title="9 · Approve Workflow Step">
      <form onSubmit={onSubmit} className="flex flex-col gap-8">
        <FormGrid>
          <EntitySelect
            label="Workflow Step"
            value={workflowStepId}
            onChange={setWorkflowStepId}
            options={stepOptions}
            error={validationErrors.workflow_step_id}
          />

          <FormField
            label="Approval Type"
            error={validationErrors.approval_type}
          >
            <TextInput
              value={approvalType}
              onChange={(e) => setApprovalType(e.target.value)}
              placeholder="FINAL"
            />
          </FormField>

          <FormField label="Approval Date">
            <TextInput
              type="date"
              value={approvalDate}
              onChange={(e) => setApprovalDate(e.target.value)}
            />
          </FormField>
        </FormGrid>

        <FormField label="Approval Notes">
          <TextareaInput
            value={approvalNotes}
            onChange={(e) => setApprovalNotes(e.target.value)}
            placeholder="Optional approval notes…"
          />
        </FormField>

        <FormError message={apiError} />
        <FormSuccess message={successMessage} />

        <SubmitButton title="Approve Workflow Step" loading={isSubmitting} />
      </form>
    </FormLayout>
  );
}
